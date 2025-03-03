#!/usr/bin/env python3
import os
import sys
import psutil
import platform
import json
import subprocess
import glob
import datetime
import time
from typing import Dict, List, Optional
import GPUtil
import asyncio

# FastAPI imports
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pydantic import BaseModel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Mining Assistant System Health Dashboard")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create static directory if it doesn't exist 
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Project base path
PROJECT_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.basename(PROJECT_BASE_PATH) != "mining-assistant":
    PROJECT_BASE_PATH = os.path.expanduser("~/mining-assistant")

# Log paths
LOGS_DIR = os.path.join(PROJECT_BASE_PATH, "logs")

# Data cache
system_data = {}
project_data = {}
services_data = {}

def get_readable_size(size_bytes):
    """Convert bytes to a human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_system_health() -> Dict:
    """Get system health information"""
    try:
        # CPU Info
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        # Memory Info
        memory = psutil.virtual_memory()
        
        # Disk Info
        disk = psutil.disk_usage('/')
        
        # Network Info
        net_io = psutil.net_io_counters()
        
        # Battery Info (if available)
        battery_info = None
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                battery_info = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secsleft": battery.secsleft
                }
        
        # GPU Info
        gpu_info = []
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                gpu_info.append({
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,  # Convert to percentage
                    "memory_total": get_readable_size(gpu.memoryTotal * 1024 * 1024),
                    "memory_used": get_readable_size(gpu.memoryUsed * 1024 * 1024),
                    "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    "temperature": gpu.temperature,
                    "uuid": gpu.uuid
                })
        except Exception as e:
            gpu_info = [{"error": str(e)}]
        
        # System Info
        system_info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "freq_current": cpu_freq.current if cpu_freq else None,
                "freq_min": cpu_freq.min if cpu_freq and hasattr(cpu_freq, 'min') else None,
                "freq_max": cpu_freq.max if cpu_freq and hasattr(cpu_freq, 'max') else None
            },
            "memory": {
                "total": get_readable_size(memory.total),
                "available": get_readable_size(memory.available),
                "used": get_readable_size(memory.used),
                "percent": memory.percent
            },
            "disk": {
                "total": get_readable_size(disk.total),
                "used": get_readable_size(disk.used),
                "free": get_readable_size(disk.free),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": get_readable_size(net_io.bytes_sent),
                "bytes_recv": get_readable_size(net_io.bytes_recv),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin if hasattr(net_io, 'dropin') else 0,
                "dropout": net_io.dropout if hasattr(net_io, 'dropout') else 0
            },
            "battery": battery_info,
            "gpu": gpu_info,
            "system_info": system_info
        }
    except Exception as e:
        return {"error": str(e)}

def get_project_health() -> Dict:
    """Get project health information"""
    try:
        # Project progress data
        progress_file = os.path.join(LOGS_DIR, ".project_progress.json")
        project_progress = {}
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                project_progress = json.load(f)
        
        # Calculate overall progress
        total_progress = 0
        if project_progress:
            for phase, phase_data in project_progress.items():
                phase_completed_steps = sum(1 for step in phase_data["steps"] if step["status"] == "completed")
                phase_in_progress_steps = sum(1 for step in phase_data["steps"] if step["status"] == "in_progress")
                phase_total_steps = len(phase_data["steps"])
                
                # Completed steps count fully, in-progress steps count half
                phase_progress = (phase_completed_steps + 0.5 * phase_in_progress_steps) / phase_total_steps * phase_data["weight"]
                total_progress += phase_progress
        
        # Find latest diagnostic report
        diagnostic_files = glob.glob(os.path.join(LOGS_DIR, "diagnostic_report_*.json"))
        latest_diagnostic = None
        
        if diagnostic_files:
            latest_diagnostic_file = max(diagnostic_files, key=os.path.getmtime)
            try:
                with open(latest_diagnostic_file, 'r') as f:
                    latest_diagnostic = json.load(f)
            except:
                pass
        
        # Find latest institutional memory
        memory_files = glob.glob(os.path.join(LOGS_DIR, "institutional_memory_*.json"))
        latest_memory = None
        memory_size = 0
        memory_item_count = 0
        
        if memory_files:
            latest_memory_file = max(memory_files, key=os.path.getmtime)
            try:
                memory_size = os.path.getsize(latest_memory_file) / 1024  # KB
                with open(latest_memory_file, 'r') as f:
                    latest_memory = json.load(f)
                    memory_item_count = len(latest_memory)
            except:
                pass
        
        # Check the important directories
        directories = [
            {"name": "Backend", "path": os.path.join(PROJECT_BASE_PATH, "backend")},
            {"name": "Frontend", "path": os.path.join(PROJECT_BASE_PATH, "frontend")},
            {"name": "Models", "path": os.path.join(PROJECT_BASE_PATH, "models")},
            {"name": "Data", "path": os.path.join(PROJECT_BASE_PATH, "data")},
            {"name": "Logs", "path": LOGS_DIR}
        ]
        
        dir_status = []
        for directory in directories:
            if os.path.exists(directory["path"]):
                try:
                    file_count = len([name for name in os.listdir(directory["path"]) 
                                    if os.path.isfile(os.path.join(directory["path"], name))])
                    size = sum(os.path.getsize(os.path.join(directory["path"], name)) 
                            for name in os.listdir(directory["path"]) 
                            if os.path.isfile(os.path.join(directory["path"], name)))
                    
                    dir_status.append({
                        "name": directory["name"],
                        "exists": True,
                        "file_count": file_count,
                        "size": get_readable_size(size)
                    })
                except Exception as e:
                    dir_status.append({
                        "name": directory["name"],
                        "exists": True,
                        "error": str(e)
                    })
            else:
                dir_status.append({
                    "name": directory["name"],
                    "exists": False
                })
        
        # Environment variables
        env_vars = {}
        important_vars = [
            "DATABASE_URL", "CLOREAI_API_KEY", "MINING_API_KEY", "ENERGY_API_KEY", 
            "MODEL_PATH", "DEVICE", "HOST", "PORT", "DEBUG", "TELEGRAM_BOT_TOKEN"
        ]
        
        for var in important_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive data
                if "API_KEY" in var or "TOKEN" in var or "PASSWORD" in var or "URL" in var:
                    if var == "DATABASE_URL" and "postgresql://" in value:
                        # Extract only the database name from the URL
                        parts = value.split("/")
                        if len(parts) > 3:
                            value = f"postgresql://****@***/{parts[-1]}"
                    else:
                        value = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
                
                env_vars[var] = value
        
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "progress": {
                "overall_percent": round(total_progress * 100, 2),
                "phases": project_progress
            },
            "diagnostic": latest_diagnostic,
            "memory": {
                "timestamp": os.path.basename(latest_memory_file) if latest_memory else None,
                "size_kb": round(memory_size, 2),
                "item_count": memory_item_count
            } if latest_memory else None,
            "directories": dir_status,
            "environment": env_vars
        }
    except Exception as e:
        return {"error": str(e)}

def get_service_status() -> Dict:
    """Get status of critical services"""
    try:
        services = [
            {"name": "PostgreSQL", "check_cmd": "systemctl is-active postgresql", "port": 5432},
            {"name": "Backend API", "check_cmd": f"pgrep -f 'python.*{os.path.join(PROJECT_BASE_PATH, 'backend/main.py')}'", "port": int(os.getenv("PORT", "8000"))},
            {"name": "Mining Connector", "service_type": "internal"},
            {"name": "Energy Connector", "service_type": "internal"},
            {"name": "CloreAI Connector", "service_type": "internal"},
        ]
        
        result = []
        for service in services:
            status = "unknown"
            info = {}
            
            if service.get("service_type") == "internal":
                # Check if any process is running with the connector name
                cmd = f"pgrep -f '{service['name'].lower().replace(' ', '_')}'"
                try:
                    subprocess.check_output(cmd, shell=True)
                    status = "active"
                except subprocess.CalledProcessError:
                    # Alternative check: look for Python processes with the connector name
                    try:
                        connector_module = service['name'].split()[0].lower() + "_connector"
                        cmd = f"pgrep -f '{connector_module}'"
                        subprocess.check_output(cmd, shell=True)
                        status = "active"
                    except subprocess.CalledProcessError:
                        status = "inactive"
            else:
                # External service check
                try:
                    subprocess.check_output(service["check_cmd"], shell=True)
                    status = "active"
                    
                    if "port" in service:
                        # Check if port is listening
                        port_cmd = f"ss -tuln | grep ':{service['port']}'"
                        try:
                            subprocess.check_output(port_cmd, shell=True)
                            info["port_status"] = "listening"
                        except subprocess.CalledProcessError:
                            info["port_status"] = "not listening"
                except subprocess.CalledProcessError:
                    status = "inactive"
            
            result.append({
                "name": service["name"],
                "status": status,
                "info": info
            })
        
        # Also get all Python processes related to the project
        python_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'mining-assistant' in cmdline:
                        python_processes.append({
                            "pid": proc.info['pid'],
                            "cmdline": cmdline
                        })
        except Exception as e:
            python_processes = [{"error": str(e)}]
        
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "services": result,
            "python_processes": python_processes
        }
    except Exception as e:
        return {"error": str(e)}

async def update_data():
    """Update all data for the dashboard"""
    global system_data, project_data, services_data
    
    while True:
        system_data = get_system_health()
        project_data = get_project_health()
        services_data = get_service_status()
        
        # Sleep for some time (shorter than the refresh interval on the frontend)
        await asyncio.sleep(30)  # 30 seconds

@app.on_event("startup")
async def startup_event():
    """Start the background task on startup"""
    asyncio.create_task(update_data())

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Render the dashboard HTML page"""
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request}
    )

@app.get("/api/system")
async def api_system():
    """API endpoint to get system health data"""
    return system_data

@app.get("/api/project")
async def api_project():
    """API endpoint to get project health data"""
    return project_data

@app.get("/api/services")
async def api_services():
    """API endpoint to get service status data"""
    return services_data

@app.get("/api/all")
async def api_all():
    """API endpoint to get all data"""
    return {
        "system": system_data,
        "project": project_data,
        "services": services_data
    }

# Create the HTML template
with open("templates/dashboard.html", "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mining Assistant System Health Dashboard</title>
    <style>
        :root {
            --primary: #3498db;
            --success: #2ecc71;
            --warning: #f39c12;
            --danger: #e74c3c;
            --info: #2980b9;
            --dark: #2c3e50;
            --light: #ecf0f1;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }
        
        .dashboard-title {
            font-size: 24px;
            font-weight: bold;
            color: var(--dark);
        }
        
        .last-updated {
            font-size: 14px;
            color: #666;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .dashboard-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
            transition: transform 0.3s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .card-header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--dark);
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        .card-content {
            font-size: 14px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px dashed #eee;
        }
        
        .status-label {
            font-weight: 500;
        }
        
        .status-value {
            text-align: right;
        }
        
        .progress-bar {
            height: 8px;
            background-color: #e0e0e0;
            border-radius: 4px;
            margin-top: 5px;
        }
        
        .progress-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .status-success {
            color: var(--success);
        }
        
        .status-warning {
            color: var(--warning);
        }
        
        .status-danger {
            color: var(--danger);
        }
        
        .status-info {
            color: var(--info);
        }
        
        .bg-success {
            background-color: var(--success);
        }
        
        .bg-warning {
            background-color: var(--warning);
        }
        
        .bg-danger {
            background-color: var(--danger);
        }
        
        .bg-info {
            background-color: var(--info);
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        
        .table th,
        .table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .table th {
            background-color: #f5f5f5;
            font-weight: 600;
        }
        
        .table tr:hover {
            background-color: #f9f9f9;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 7px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        
        .badge-success {
            background-color: var(--success);
        }
        
        .badge-warning {
            background-color: var(--warning);
        }
        
        .badge-danger {
            background-color: var(--danger);
        }
        
        .badge-info {
            background-color: var(--info);
        }
        
        .badge-dark {
            background-color: var(--dark);
        }
        
        .expand-button {
            background: none;
            border: none;
            color: var(--primary);
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        
        .hidden {
            display: none;
        }
        
        .gpu-card {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f5f5f5;
        }
        
        .gpu-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .refresh-button {
            padding: 10px 20px;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .refresh-button:hover {
            background-color: var(--info);
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .dashboard-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .last-updated {
                margin-top: 10px;
            }
        }

        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1a1a1a;
                color: #f0f0f0;
            }
            
            .dashboard-card {
                background: #2a2a2a;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            }
            
            .card-header {
                color: #e0e0e0;
                border-bottom-color: #444;
            }
            
            .status-item {
                border-bottom-color: #444;
            }
            
            .table th {
                background-color: #333;
            }
            
            .table td {
                border-bottom-color: #444;
            }
            
            .table tr:hover {
                background-color: #333;
            }
            
            .gpu-card {
                background-color: #333;
            }
            
            .progress-bar {
                background-color: #444;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="dashboard-header">
            <h1 class="dashboard-title">Mining Assistant System Health Dashboard</h1>
            <div>
                <span class="last-updated">Last updated: <span id="last-updated-time">Loading...</span></span>
                <button id="refresh-button" class="refresh-button">Refresh Now</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Health Card -->
            <div class="dashboard-card">
                <h2 class="card-header">System Health</h2>
                <div class="card-content" id="system-health">
                    <div class="status-item">
                        <span class="status-label">CPU Usage</span>
                        <span class="status-value" id="cpu-usage">Loading...</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" id="cpu-progress" style="width: 0%;"></div>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">Memory Usage</span>
                        <span class="status-value" id="memory-usage">Loading...</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" id="memory-progress" style="width: 0%;"></div>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">Disk Usage</span>
                        <span class="status-value" id="disk-usage">Loading...</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" id="disk-progress" style="width: 0%;"></div>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">Network I/O</span>
                        <span class="status-value" id="network-io">Loading...</span>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">System Uptime</span>
                        <span class="status-value" id="system-uptime">Loading...</span>
                    </div>
                    
                    <button class="expand-button" id="system-expand-btn">Show More Details</button>
                    
                    <div id="system-details" class="hidden">
                        <div class="status-item">
                            <span class="status-label">OS</span>
                            <span class="status-value" id="system-os">Loading...</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Python Version</span>
                            <span class="status-value" id="python-version">Loading...</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">CPU Cores</span>
                            <span class="status-value" id="cpu-cores">Loading...</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">CPU Frequency</span>
                            <span class="status-value" id="cpu-freq">Loading...</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- GPU Status Card -->
            <div class="dashboard-card">
                <h2 class="card-header">GPU Status</h2>
                <div class="card-content" id="gpu-status">
                    <div id="gpu-list">Loading GPU information...</div>
                </div>
            </div>
            
            <!-- Project Health Card -->
            <div class="dashboard-card">
                <h2 class="card-header">Project Health</h2>
                <div class="card-content" id="project-health">
                    <div class="status-item">
                        <span class="status-label">Overall Progress</span>
                        <span class="status-value" id="project-progress">Loading...</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill bg-info" id="project-progress-bar" style="width: 0%;"></div>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">Institutional Memory</span>
                        <span class="status-value" id="institutional-memory">Loading...</span>
                    </div>
                    
                    <div class="status-item">
                        <span class="status-label">Database Status</span>
                        <span class="status-value" id="database-status">Loading...</span>
                    </div>
                    
                    <button class="expand-button" id="project-expand-btn">Show Project Phases</button>
                    
                    <div id="project-phases" class="hidden">
                        <table class="table" id="phases-table">
                            <thead>
                                <tr>
                                    <th>Phase</th>
                                    <th>Status</th>
                                    <th>Weight</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Will be populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Services Status Card -->
            <div class="dashboard-card">
                <h2 class="card-header">Services Status</h2>
                <div class="card-content" id="services-status">
                    <table class="table" id="services-table">
                        <thead>
                            <tr>
                                <th>Service</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Will be populated by JavaScript -->
                        </tbody>
                    </table>
                    
                    <button class="expand-button" id="services-expand-btn">Show Python Processes</button>
                    
                    <div id="python-processes" class="hidden">
                        <h3 style="margin-top: 15px; margin-bottom: 10px;">Python Processes</h3>
                        <div id="python-processes-list">
                            <!-- Will be populated by JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Environment Variables Card -->
            <div class="dashboard-card">
                <h2 class="card-header">Environment</h2>
                <div class="card-content" id="environment">
                    <table class="table" id="env-table">
                        <thead>
                            <tr>
                                <th>Variable</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Will be populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Directory Status Card -->
            <div class="dashboard-card">
                <h2 class="card-header">Directory Status</h2>
                <div class="card-content" id="directory-status">
                    <table class="table" id="dir-table">
                        <thead>
                            <tr>
                                <th>Directory</th>
                                <th>Status</th>
                                <th>Files</th>
                                <th>Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Will be populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        const refreshInterval = 60000; // 1 minute
        let refreshTimer;
        
        // DOM Elements
        const lastUpdatedTime = document.getElementById('last-updated-time');
        const refreshButton = document.getElementById('refresh-button');
        
        // Expand buttons
        const systemExpandBtn = document.getElementById('system-expand-btn');
        const systemDetails = document.getElementById('system-details');
        const projectExpandBtn = document.getElementById('project-expand-btn');
        const projectPhases = document.getElementById('project-phases');
        const servicesExpandBtn = document.getElementById('services-expand-btn');
        const pythonProcesses = document.getElementById('python-processes');
        
        // Bind click events for expand buttons
        systemExpandBtn.addEventListener('click', () => {
            systemDetails.classList.toggle('hidden');
            systemExpandBtn.textContent = systemDetails.classList.contains('hidden') 
                ? 'Show More Details' 
                : 'Hide Details';
        });
        
        projectExpandBtn.addEventListener('click', () => {
            projectPhases.classList.toggle('hidden');
            projectExpandBtn.textContent = projectPhases.classList.contains('hidden') 
                ? 'Show Project Phases' 
                : 'Hide Project Phases';
        });
        
        servicesExpandBtn.addEventListener('click', () => {
            pythonProcesses.classList.toggle('hidden');
            servicesExpandBtn.textContent = pythonProcesses.classList.contains('hidden') 
                ? 'Show Python Processes' 
                : 'Hide Python Processes';
        });
        
        // Helper function to get status color class
        function getStatusClass(value, thresholds) {
            if (value >= thresholds.danger) return 'status-danger';
            if (value >= thresholds.warning) return 'status-warning';
            return 'status-success';
        }
        
        // Helper function to get background color class
        function getBgClass(value, thresholds) {
            if (value >= thresholds.danger) return 'bg-danger';
            if (value >= thresholds.warning) return 'bg-warning';
            return 'bg-success';
        }
        
        // Helper function to format date difference
        function formatTimeDiff(startDateStr) {
            const startDate = new Date(startDateStr);
            const now = new Date();
            const diffMs = now - startDate;
            
            const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
            
            if (days > 0) {
                return `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }
        
        // Update System Health Section
        function updateSystemHealth(data) {
            if (!data || data.error) {
                document.getElementById('system-health').innerHTML = `<div class="status-danger">Error: ${data?.error || 'Failed to load system data'}</div>`;
                return;
            }
            
            // CPU Usage
            const cpuPercent = data.cpu.percent;
            document.getElementById('cpu-usage').textContent = `${cpuPercent.toFixed(1)}%`;
            document.getElementById('cpu-usage').className = `status-value ${getStatusClass(cpuPercent, {warning: 70, danger: 90})}`;
            document.getElementById('cpu-progress').style.width = `${cpuPercent}%`;
            document.getElementById('cpu-progress').className = `progress-bar-fill ${getBgClass(cpuPercent, {warning: 70, danger: 90})}`;
            
            // Memory Usage
            const memoryPercent = data.memory.percent;
            document.getElementById('memory-usage').textContent = `${memoryPercent.toFixed(1)}% (${data.memory.used} / ${data.memory.total})`;
            document.getElementById('memory-usage').className = `status-value ${getStatusClass(memoryPercent, {warning: 70, danger: 90})}`;
            document.getElementById('memory-progress').style.width = `${memoryPercent}%`;
            document.getElementById('memory-progress').className = `progress-bar-fill ${getBgClass(memoryPercent, {warning: 70, danger: 90})}`;
            
            // Disk Usage
            const diskPercent = data.disk.percent;
            document.getElementById('disk-usage').textContent = `${diskPercent.toFixed(1)}% (${data.disk.used} / ${data.disk.total})`;
            document.getElementById('disk-usage').className = `status-value ${getStatusClass(diskPercent, {warning: 70, danger: 90})}`;
            document.getElementById('disk-progress').style.width = `${diskPercent}%`;
            document.getElementById('disk-progress').className = `progress-bar-fill ${getBgClass(diskPercent, {warning: 70, danger: 90})}`;
            
            // Network I/O
            document.getElementById('network-io').textContent = `↓ ${data.network.bytes_recv} | ↑ ${data.network.bytes_sent}`;
            
            // System Uptime
            document.getElementById('system-uptime').textContent = formatTimeDiff(data.system_info.boot_time);
            
            // More details
            document.getElementById('system-os').textContent = `${data.system_info.system} ${data.system_info.release}`;
            document.getElementById('python-version').textContent = data.system_info.python_version;
            document.getElementById('cpu-cores').textContent = data.cpu.count;
            document.getElementById('cpu-freq').textContent = data.cpu.freq_current ? `${data.cpu.freq_current.toFixed(1)} MHz` : 'N/A';
        }
        
        // Update GPU Status Section
        function updateGpuStatus(data) {
            const gpuList = document.getElementById('gpu-list');
            
            if (!data || !data.gpu || data.error) {
                gpuList.innerHTML = '<div class="status-warning">No GPU data available</div>';
                return;
            }
            
            if (data.gpu.length === 0) {
                gpuList.innerHTML = '<div class="status-warning">No GPUs detected</div>';
                return;
            }
            
            let gpuHtml = '';
            
            data.gpu.forEach((gpu, index) => {
                if (gpu.error) {
                    gpuHtml += `<div class="gpu-card"><div class="status-danger">Error: ${gpu.error}</div></div>`;
                    return;
                }
                
                const loadClass = getStatusClass(gpu.load, {warning: 70, danger: 90});
                const memoryClass = getStatusClass(gpu.memory_percent, {warning: 70, danger: 90});
                const tempClass = getStatusClass(gpu.temperature, {warning: 70, danger: 85});
                
                gpuHtml += `
                    <div class="gpu-card">
                        <div class="gpu-name">${gpu.name}</div>
                        <div class="status-item">
                            <span class="status-label">Load</span>
                            <span class="status-value ${loadClass}">${gpu.load.toFixed(1)}%</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Memory</span>
                            <span class="status-value ${memoryClass}">${gpu.memory_percent.toFixed(1)}% (${gpu.memory_used} / ${gpu.memory_total})</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Temperature</span>
                            <span class="status-value ${tempClass}">${gpu.temperature.toFixed(1)}°C</span>
                        </div>
                    </div>
                `;
            });
            
            gpuList.innerHTML = gpuHtml;
        }
        
        // Update Project Health Section
        function updateProjectHealth(data) {
            if (!data || data.error) {
                document.getElementById('project-health').innerHTML = `<div class="status-danger">Error: ${data?.error || 'Failed to load project data'}</div>`;
                return;
            }
            
            // Overall Progress
            const progress = data.progress?.overall_percent || 0;
            document.getElementById('project-progress').textContent = `${progress}%`;
            document.getElementById('project-progress-bar').style.width = `${progress}%`;
            
            // Institutional Memory
            if (data.memory) {
                document.getElementById('institutional-memory').textContent = `${data.memory.item_count} items, ${data.memory.size_kb} KB`;
            } else {
                document.getElementById('institutional-memory').textContent = 'Not available';
                document.getElementById('institutional-memory').className = 'status-value status-warning';
            }
            
            // Database Status
            const dbConnectionStatus = data.diagnostic?.database?.status || 'unknown';
            let dbStatusText = 'Unknown';
            let dbStatusClass = 'status-warning';
            
            if (dbConnectionStatus === 'connected') {
                const tables = data.diagnostic?.database?.tables || [];
                dbStatusText = `Connected (${tables.length} tables)`;
                dbStatusClass = 'status-success';
            } else if (dbConnectionStatus === 'disconnected') {
                dbStatusText = 'Disconnected';
                dbStatusClass = 'status-danger';
            }
            
            document.getElementById('database-status').textContent = dbStatusText;
            document.getElementById('database-status').className = `status-value ${dbStatusClass}`;
            
            // Project Phases
            const phasesTable = document.getElementById('phases-table').querySelector('tbody');
            phasesTable.innerHTML = '';
            
            if (data.progress && data.progress.phases) {
                Object.entries(data.progress.phases).forEach(([phaseName, phaseData]) => {
                    const completedSteps = phaseData.steps.filter(step => step.status === 'completed').length;
                    const inProgressSteps = phaseData.steps.filter(step => step.status === 'in_progress').length;
                    const totalSteps = phaseData.steps.length;
                    
                    let phaseStatus = '';
                    let statusClass = '';
                    
                    if (completedSteps === totalSteps) {
                        phaseStatus = 'Completed';
                        statusClass = 'badge-success';
                    } else if (completedSteps > 0 || inProgressSteps > 0) {
                        phaseStatus = 'In Progress';
                        statusClass = 'badge-info';
                    } else {
                        phaseStatus = 'Pending';
                        statusClass = 'badge-warning';
                    }
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${phaseName}</td>
                        <td><span class="badge ${statusClass}">${phaseStatus}</span> (${completedSteps}/${totalSteps})</td>
                        <td>${(phaseData.weight * 100).toFixed(0)}%</td>
                    `;
                    phasesTable.appendChild(row);
                });
            }
        }
        
        // Update Services Status Section
        function updateServicesStatus(data) {
            if (!data || data.error) {
                document.getElementById('services-status').innerHTML = `<div class="status-danger">Error: ${data?.error || 'Failed to load services data'}</div>`;
                return;
            }
            
            // Services Table
            const servicesTable = document.getElementById('services-table').querySelector('tbody');
            servicesTable.innerHTML = '';
            
            if (data.services && data.services.length > 0) {
                data.services.forEach(service => {
                    const row = document.createElement('tr');
                    
                    let statusBadgeClass = 'badge-warning';
                    if (service.status === 'active') {
                        statusBadgeClass = 'badge-success';
                    } else if (service.status === 'inactive') {
                        statusBadgeClass = 'badge-danger';
                    }
                    
                    row.innerHTML = `
                        <td>${service.name}</td>
                        <td><span class="badge ${statusBadgeClass}">${service.status}</span></td>
                    `;
                    servicesTable.appendChild(row);
                });
            } else {
                servicesTable.innerHTML = '<tr><td colspan="2">No services found</td></tr>';
            }
            
            // Python Processes
            const processesList = document.getElementById('python-processes-list');
            
            if (data.python_processes && data.python_processes.length > 0) {
                let processesHtml = '<ul style="list-style-type: none; padding-left: 0;">';
                
                data.python_processes.forEach(process => {
                    if (process.error) {
                        processesHtml += `<li class="status-danger">Error: ${process.error}</li>`;
                    } else {
                        processesHtml += `<li><strong>PID ${process.pid}</strong>: ${process.cmdline}</li>`;
                    }
                });
                
                processesHtml += '</ul>';
                processesList.innerHTML = processesHtml;
            } else {
                processesList.innerHTML = '<div class="status-warning">No Python processes found</div>';
            }
        }
        
        // Update Environment Variables Section
        function updateEnvironment(data) {
            if (!data || data.error || !data.environment) {
                document.getElementById('environment').innerHTML = `<div class="status-warning">No environment data available</div>`;
                return;
            }
            
            const envTable = document.getElementById('env-table').querySelector('tbody');
            envTable.innerHTML = '';
            
            Object.entries(data.environment).forEach(([key, value]) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${key}</td>
                    <td>${value}</td>
                `;
                envTable.appendChild(row);
            });
            
            if (Object.keys(data.environment).length === 0) {
                envTable.innerHTML = '<tr><td colspan="2">No environment variables available</td></tr>';
            }
        }
        
        // Update Directory Status Section
        function updateDirectoryStatus(data) {
            if (!data || data.error || !data.directories) {
                document.getElementById('directory-status').innerHTML = `<div class="status-warning">No directory data available</div>`;
                return;
            }
            
            const dirTable = document.getElementById('dir-table').querySelector('tbody');
            dirTable.innerHTML = '';
            
            data.directories.forEach(dir => {
                const row = document.createElement('tr');
                
                let statusBadge = '';
                let fileCount = '';
                let size = '';
                
                if (dir.exists) {
                    statusBadge = '<span class="badge badge-success">Exists</span>';
                    fileCount = dir.error ? 'Error' : dir.file_count;
                    size = dir.error ? dir.error : dir.size;
                } else {
                    statusBadge = '<span class="badge badge-danger">Missing</span>';
                    fileCount = 'N/A';
                    size = 'N/A';
                }
                
                row.innerHTML = `
                    <td>${dir.name}</td>
                    <td>${statusBadge}</td>
                    <td>${fileCount}</td>
                    <td>${size}</td>
                `;
                dirTable.appendChild(row);
            });
        }
        
        // Fetch all data and update the dashboard
        function updateDashboard() {
            fetch('/api/all')
                .then(response => response.json())
                .then(data => {
                    // Update last updated time
                    lastUpdatedTime.textContent = new Date().toLocaleString();
                    
                    // Update each section
                    updateSystemHealth(data.system);
                    updateGpuStatus(data.system);
                    updateProjectHealth(data.project);
                    updateServicesStatus(data.services);
                    updateEnvironment(data.project);
                    updateDirectoryStatus(data.project);
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                    alert('Failed to update dashboard. Check console for details.');
                });
        }
        
        // Start automatic refresh
        function startAutoRefresh() {
            // Clear any existing timer
            if (refreshTimer) {
                clearInterval(refreshTimer);
            }
            
            // Set new timer
            refreshTimer = setInterval(updateDashboard, refreshInterval);
        }
        
        // Initialize dashboard
        function initDashboard() {
            // Initial update
            updateDashboard();
            
            // Start auto-refresh
            startAutoRefresh();
            
            // Refresh button click handler
            refreshButton.addEventListener('click', () => {
                updateDashboard();
                // Reset auto-refresh timer
                startAutoRefresh();
            });
        }
        
        // Start dashboard when DOM is loaded
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>""")


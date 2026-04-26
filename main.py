from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
import base64
import glob as _glob
import json
import math
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile
from collections import deque

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PYZ_EXTRACTED_DIR = os.path.join(THIS_DIR, "PYZ.pyz_extracted")


sys.modules.setdefault("main", sys.modules[__name__])


if os.path.isdir(PYZ_EXTRACTED_DIR) and PYZ_EXTRACTED_DIR not in sys.path:
    sys.path.append(PYZ_EXTRACTED_DIR)


def find_config_dir():
    candidates = []

    if getattr(sys, "frozen", False):
        try:
            candidates.append(os.path.dirname(os.path.abspath(sys.executable)))
        except Exception:
            pass

    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass

    candidates.append(os.getcwd())

    for start_path in candidates:
        current = start_path

        while current:
            config_file = os.path.join(current, "main_config.json")
            app_py = os.path.join(current, "app.py")
            app_exe_win = os.path.join(current, "app.exe")
            app_exe_lin = os.path.join(current, "app")
            dist_exe_win = os.path.join(current, "dist", "app.exe")
            dist_exe_lin = os.path.join(current, "dist", "app")

            config_exists = os.path.exists(config_file)
            app_exists = (
                os.path.exists(app_py)
                or os.path.exists(app_exe_win)
                or os.path.exists(app_exe_lin)
                or os.path.exists(dist_exe_win)
                or os.path.exists(dist_exe_lin)
                or os.path.isdir(os.path.join(current, "setup_webui_extracted"))
                or (
                    os.path.isdir(os.path.join(current, "templates"))
                    and os.path.isdir(os.path.join(current, "static"))
                )
            )

            if app_exists:
                return current

            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

    return os.getcwd()


BASE_DIR = find_config_dir()
FALLBACK_PROJECT_DIR = os.path.join(BASE_DIR, "setupUI_runtime")
FALLBACK_APP_PY_PATH = os.path.join(FALLBACK_PROJECT_DIR, "app.py")


def _select_runtime_base_dir():
    core_files = ["app.py", "main_config.json", "objects.json", "ar_receiver.py"]
    dist_dir = os.path.join(BASE_DIR, "dist")
    if os.path.isdir(dist_dir) and all(
        os.path.exists(os.path.join(dist_dir, name)) for name in core_files
    ):
        return dist_dir
    if os.path.isdir(FALLBACK_PROJECT_DIR) and all(
        os.path.exists(os.path.join(FALLBACK_PROJECT_DIR, name)) for name in core_files
    ):
        return FALLBACK_PROJECT_DIR
    return BASE_DIR


RUNTIME_BASE_DIR = _select_runtime_base_dir()

WEBUI_VERSION = {
    "name": "X-Verse Setup WebUI",
    "version": "1.1.4",
    "build": "2026-04-12",
}


def _resolve_asset_dir(name):
    candidates = []
    seen = set()

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, name))

    candidates.extend(
        [
            os.path.join(THIS_DIR, name),
            os.path.join(RUNTIME_BASE_DIR, name),
            os.path.join(BASE_DIR, name),
            os.path.join(os.path.dirname(THIS_DIR), "setup_webui_extracted", name),
            os.path.join(BASE_DIR, "setup_webui_extracted", name),
        ]
    )

    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isdir(candidate):
            return candidate

    return None


template_folder = _resolve_asset_dir("templates")
static_folder = _resolve_asset_dir("static")

app_kwargs = {}
if template_folder:
    app_kwargs["template_folder"] = template_folder
if static_folder:
    app_kwargs["static_folder"] = static_folder

app = Flask(__name__, **app_kwargs)

APP_PY_PATH = os.path.join(RUNTIME_BASE_DIR, "app.py")
CONFIG_PATH = os.path.join(RUNTIME_BASE_DIR, "main_config.json")

app.config["MAX_CONTENT_LENGTH"] = 524288000


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        return ip
    finally:
        s.close()


@app.route("/")
def index():
    return render_template("index.html", ip=get_ip())


@app.route("/favicon.ico")
def favicon():
    return "", 204


engine_process = None
log_buffer = deque(maxlen=200)


def output_reader(proc):
    for line in iter(proc.stdout.readline, ""):
        try:
            log_buffer.append(line)
        except Exception:
            pass


@app.route("/api/status", methods=["GET"])
def get_status():
    is_running = engine_process is not None and engine_process.poll() is None
    return jsonify({"running": is_running})


@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": list(log_buffer)})


@app.route("/api/version", methods=["GET"])
def get_version():
    engine = {
        "name": "AR Engine",
        "version": "5.1.4",
        "build": "unknown",
        "path": APP_PY_PATH,
    }
    version_path = os.path.join(RUNTIME_BASE_DIR, "engine_version.json")

    try:
        if os.path.exists(version_path):
            with open(version_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            engine.update(
                {
                    "name": data.get("name", engine["name"]),
                    "version": data.get("version", engine["version"]),
                    "build": data.get("build", engine["build"]),
                    "path": version_path,
                }
            )
    except Exception as e:
        engine["version"] = f"error: {e}"

    return jsonify({"success": True, "webui": WEBUI_VERSION, "engine": engine})


@app.route("/api/stop", methods=["POST"])
def stop_app():
    global engine_process, preview_process

    if engine_process is not None and engine_process.poll() is None:
        import signal

        if preview_process is not None and preview_process.poll() is None:
            try:
                if os.name == "nt":
                    os.kill(preview_process.pid, signal.CTRL_C_EVENT)
                else:
                    os.killpg(os.getpgid(preview_process.pid), signal.SIGTERM)
                preview_process.wait(timeout=2)
            except Exception:
                try:
                    preview_process.kill()
                except Exception:
                    pass
            preview_process = None

        try:
            try:
                if os.name == "nt":
                    os.kill(engine_process.pid, signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
                engine_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    try:
                        os.killpg(os.getpgid(engine_process.pid), signal.SIGKILL)
                    except Exception:
                        pass
                engine_process.kill()
            except Exception:
                engine_process.kill()
        finally:
            engine_process = None

            try:
                from multiprocessing import shared_memory

                old_shm = shared_memory.SharedMemory(name="shm_ar_video")
                old_shm.close()
                old_shm.unlink()
                log_buffer.append("[WebUI] Cleaned up shared memory segment.\n")
            except Exception:
                pass

            log_buffer.append("[WebUI] System stopped by user.\n")

        return jsonify({"success": True, "message": "System stopped."})

    return jsonify({"success": False, "error": "System is not running."})


def extract_archive(filepath, target_dir):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".zip":
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(target_dir)
            return True, "Success"
        return False, f"Unsupported format: {ext} (Please use .zip)"
    except Exception as e:
        return False, str(e)


@app.route("/api/import_preset", methods=["POST"])
def import_preset():
    data = request.get_json(silent=True) or {}
    preset_name = data.get("preset", "标准赛道A")

    target_extract_dir = RUNTIME_BASE_DIR
    preset_path = os.path.join(target_extract_dir, f"{preset_name}.zip")

    if not os.path.exists(preset_path):
        return jsonify({"success": False, "error": "Preset archive not found"})

    success, msg = extract_archive(preset_path, target_extract_dir)
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": msg})


@app.route("/api/check_preset", methods=["GET"])
def check_preset():
    preset_names = [
        "标准赛道A",
        "娱乐赛道B",
        "正式赛道-区域赛",
        "正式赛道-总决赛",
        "探险赛道C",
        "塔防赛道D",
    ]
    available_presets = []
    target_extract_dir = RUNTIME_BASE_DIR

    for name in preset_names:
        preset_path = os.path.join(target_extract_dir, f"{name}.zip")
        if os.path.exists(preset_path):
            available_presets.append(name)

    return jsonify({"success": True, "available": available_presets})


@app.route("/api/upload_preset_zip", methods=["POST"])
def upload_preset_zip():
    if "archive" not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files["archive"]
    preset_name = request.form.get("preset_name")

    if not preset_name:
        return jsonify({"success": False, "error": "Missing preset name"})

    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"})

    if not file.filename.lower().endswith(".zip"):
        return jsonify({"success": False, "error": "Only .zip is supported."})

    target_extract_dir = RUNTIME_BASE_DIR
    target_path = os.path.join(target_extract_dir, f"{preset_name}.zip")

    try:
        if os.path.exists(target_path):
            os.remove(target_path)
        file.save(target_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/download_loc_format", methods=["GET"])
def download_loc_format():
    format_data = {
        "id": "car_01",
        "timestamp": 1678888888.123,
        "x": 1.23,
        "y": 0.0,
        "z": -4.56,
        "pitch": 0.0,
        "yaw": 90.0,
        "roll": 0.0,
    }

    action = request.args.get("action", "view")
    if action == "download":
        return app.response_class(
            response=json.dumps(format_data, indent=4),
            status=200,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=location_format.json"},
        )

    return jsonify(format_data)


@app.route("/api/upload_scene", methods=["POST"])
def upload_scene():
    if "archive" not in request.files:
        return jsonify({"success": False, "error": "No file part"})

    file = request.files["archive"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"})

    if not file.filename.lower().endswith(".zip"):
        return jsonify(
            {"success": False, "error": "Only .zip is supported on edge devices."}
        )

    target_extract_dir = RUNTIME_BASE_DIR
    temp_path = os.path.join(
        target_extract_dir,
        "temp_scene_upload" + os.path.splitext(file.filename)[1],
    )

    try:
        file.save(temp_path)
        success, msg = extract_archive(temp_path, target_extract_dir)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if success:
            return jsonify({"success": True})
        return jsonify({"success": False, "error": msg})
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/upload_engine", methods=["POST"])
def upload_engine():
    if engine_process is not None and engine_process.poll() is None:
        return jsonify({"success": False, "error": "请先停止系统再升级引擎！"})

    if "engine" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    file = request.files["engine"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"})

    exe_name = "app.exe" if os.name == "nt" else "app"
    target_path = os.path.join(RUNTIME_BASE_DIR, exe_name)
    dist_target = os.path.join(RUNTIME_BASE_DIR, "dist", exe_name)

    if os.path.exists(dist_target):
        final_path = dist_target
    elif os.path.exists(target_path):
        final_path = target_path
    else:
        final_path = dist_target

    try:
        if os.path.exists(final_path):
            os.remove(final_path)

        file.save(final_path)

        if os.name != "nt":
            os.chmod(final_path, 0o755)

        return jsonify({"success": True, "path": os.path.basename(final_path)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/self_update", methods=["POST"])
def self_update():
    if "webui" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    file = request.files["webui"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected"})

    exe_name = "setup_webui.exe" if os.name == "nt" else "setup_webui"
    if getattr(sys, "frozen", False) and os.path.basename(sys.executable) == exe_name:
        target_path = sys.executable
    else:
        target_path = os.path.join(RUNTIME_BASE_DIR, exe_name)

    temp_path = target_path + ".upload"

    try:
        file.save(temp_path)

        if os.name != "nt":
            os.chmod(temp_path, 0o755)

        os.replace(temp_path, target_path)
        return jsonify({"success": True, "path": target_path})
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/config", methods=["GET"])
def get_config():
    if not os.path.exists(CONFIG_PATH):
        return jsonify({"success": True, "config": {"network": {}}})

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"success": True, "config": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/config", methods=["POST"])
def save_config():
    req_data = request.get_json(silent=True) or {}

    try:
        if not os.path.exists(CONFIG_PATH):
            data = {}
        else:
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        if "network" not in data:
            data["network"] = {}

        net = data["network"]
        valid_keys = [
            "udp_target_ip",
            "udp_target_port",
            "unity_target_ip",
            "unity_sync_port",
        ]

        for key in valid_keys:
            if key in req_data:
                val = req_data[key]
                if "port" in key:
                    val = int(val)
                net[key] = val

        if "pos_offset" in req_data:
            net["pos_offset"] = [float(v) for v in req_data["pos_offset"]]

        if "euler_offset" in req_data:
            net["euler_offset"] = [float(v) for v in req_data["euler_offset"]]

        if "movement_delay_ms" in req_data:
            delay = int(req_data["movement_delay_ms"])
            net["movement_delay_ms"] = max(0, min(delay, 500))

        if "video_flip" in req_data and isinstance(req_data["video_flip"], dict):
            flip = req_data["video_flip"]
            data["video_flip"] = {
                "horizontal": bool(flip.get("horizontal", False)),
                "vertical": bool(flip.get("vertical", False)),
            }

        if "K" in req_data:
            k = req_data["K"]
            if not isinstance(k, list) or len(k) != 3:
                raise ValueError("K must be a 3x3 matrix")
            data["K"] = [[float(v) for v in row] for row in k]
            if any(len(row) != 3 for row in data["K"]):
                raise ValueError("K must be a 3x3 matrix")

        if "D" in req_data:
            d = req_data["D"]
            if not isinstance(d, list) or len(d) < 5:
                raise ValueError("D must contain at least 5 values")
            data["D"] = [float(v) for v in d[:5]]

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def clean_pyinstaller_env(env):
    if getattr(sys, "frozen", False):
        if "LD_LIBRARY_PATH_ORIG" in env:
            env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
        else:
            env.pop("LD_LIBRARY_PATH", None)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
    return env


def configure_engine_render_env(env):
    machine = platform.machine().lower()
    gl4es_dir = "/opt/gl4es"
    gl4es_lib = os.path.join(gl4es_dir, "libGL.so.1")
    if (
        os.name != "nt"
        and machine in {"aarch64", "arm64"}
        and os.path.exists(gl4es_lib)
    ):
        ld_paths = [gl4es_dir]
        existing_ld = env.get("LD_LIBRARY_PATH", "")
        if existing_ld:
            ld_paths.extend(p for p in existing_ld.split(":") if p and p != gl4es_dir)
        env["LD_LIBRARY_PATH"] = ":".join(ld_paths)
        env["LIBGL_ES"] = "2"
        env.pop("LIBGL_ALWAYS_SOFTWARE", None)
        return "gl4es"

    env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    env.pop("LIBGL_ES", None)
    return "software"


@app.route("/api/launch", methods=["POST"])
def launch_app():
    global engine_process

    if engine_process is not None and engine_process.poll() is None:
        return jsonify({"success": False, "error": "System is already running!"})

    log_buffer.clear()

    exe_name = "app.exe" if os.name == "nt" else "app"
    app_exe_path = os.path.join(RUNTIME_BASE_DIR, exe_name)
    dist_exe_path = os.path.join(RUNTIME_BASE_DIR, "dist", exe_name)
    app_py_path = os.path.join(RUNTIME_BASE_DIR, "app.py")
    source_candidates = []
    for candidate in [app_py_path, FALLBACK_APP_PY_PATH]:
        if candidate not in source_candidates:
            source_candidates.append(candidate)
    preferred_app_py_path = next(
        (candidate for candidate in source_candidates if os.path.exists(candidate)),
        None,
    )

    command = None

    if preferred_app_py_path is not None:
        python_exe = "python" if os.name == "nt" else "python3"
        if getattr(sys, "frozen", False) == False:
            python_exe = sys.executable

        command = [python_exe, "-u", preferred_app_py_path]
        log_buffer.append("[*] Found Python engine script.\n")
    elif os.path.exists(app_exe_path):
        command = [app_exe_path]
        log_buffer.append("[*] Found compiled engine.\n")
    elif os.path.exists(dist_exe_path):
        command = [dist_exe_path]
        log_buffer.append("[*] Found compiled engine.\n")
    else:
        return jsonify(
            {
                "success": False,
                "error": f"未找到引擎! (Searched for {exe_name} or app.py)",
            }
        )

    try:
        render_backend = "default"
        if os.name == "nt":
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env = clean_pyinstaller_env(env)
        else:
            env = get_active_x11_env()
            render_backend = configure_engine_render_env(env)
            env.setdefault("DISPLAY", ":0")
            env.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

        log_buffer.append(
            "[*] Launch env:"
            f" backend={render_backend}"
            f" LIBGL_ALWAYS_SOFTWARE={env.get('LIBGL_ALWAYS_SOFTWARE', '')}"
            f" LIBGL_ES={env.get('LIBGL_ES', '')}"
            "\n"
        )

        kwargs = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["preexec_fn"] = os.setsid

        def try_launch(cmd):
            proc = subprocess.Popen(
                cmd,
                cwd=RUNTIME_BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                text=True,
                env=env,
                **kwargs,
            )
            try:
                proc.wait(timeout=1.5)
                return proc, False
            except subprocess.TimeoutExpired:
                return proc, True

        engine_process, inst_alive = try_launch(command)

        compiled_paths = [app_exe_path, dist_exe_path]
        if (
            not inst_alive
            and engine_process.returncode != 0
            and any(path in command for path in compiled_paths)
            and os.path.exists(preferred_app_py_path)
        ):
            log_buffer.append(
                f"[!] Compiled engine failed (return code {engine_process.returncode}). Falling back to python script...\n"
            )

            if os.name == "nt":
                command = [sys.executable, "-u", preferred_app_py_path]
            else:
                command = ["python3", "-u", preferred_app_py_path]

            engine_process, inst_alive = try_launch(command)

        t = threading.Thread(target=output_reader, args=(engine_process,), daemon=True)
        t.start()

        return jsonify(
            {"success": True, "message": "App launch requested successfully!"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


preview_process = None


def _detect_display_from_proc():
    import re

    target_procs = [
        "Xvnc",
        "x0vncserver",
        "xfce4-session",
        "gnome-session",
        "mate-session",
        "lxsession",
        "plasmashell",
        "openbox",
        "fluxbox",
        "pcmanfm",
    ]

    found_displays = {}

    for proc_name in target_procs:
        try:
            pids = (
                subprocess.check_output(
                    ["pgrep", "-x", proc_name], stderr=subprocess.DEVNULL
                )
                .decode()
                .strip()
                .split("\n")
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

        for pid in pids:
            pid = pid.strip()
            if not pid:
                continue

            try:
                with open(f"/proc/{pid}/environ", "rb") as f:
                    raw = f.read().decode("utf-8", errors="ignore")

                dm = re.search(r"(?:^|\x00)DISPLAY=(:[^\x00]+)", raw)
                if dm:
                    disp = dm.group(1)
                    xm = re.search(r"(?:^|\x00)XAUTHORITY=([^\x00]+)", raw)
                    xauth = xm.group(1) if xm else None
                    found_displays[disp] = xauth
            except (PermissionError, FileNotFoundError, OSError):
                continue

    if not found_displays:
        return None, None

    for disp, xauth in found_displays.items():
        if disp != ":0" and not disp.startswith(":0."):
            return disp, xauth

    first_disp = next(iter(found_displays))
    return first_disp, found_displays[first_disp]


def _detect_display_from_x11_sockets():
    sockets = sorted(_glob.glob("/tmp/.X11-unix/X*"))
    if not sockets:
        return None

    displays = [":" + s.split("/X")[-1] for s in sockets]
    for disp in displays:
        if disp != ":0":
            return disp
    return displays[0]


def get_active_x11_env():
    env = os.environ.copy()
    env = clean_pyinstaller_env(env)

    if os.name == "nt":
        return env

    env["PYTHONUNBUFFERED"] = "1"
    env["QT_X11_NO_MITSHM"] = "1"

    proc_display, proc_xauth = _detect_display_from_proc()
    if proc_display:
        env["DISPLAY"] = proc_display
        env["XAUTHORITY"] = proc_xauth or os.path.expanduser("~/.Xauthority")
        return env

    socket_display = _detect_display_from_x11_sockets()
    if socket_display:
        env["DISPLAY"] = socket_display
        env["XAUTHORITY"] = os.path.expanduser("~/.Xauthority")
        return env

    if env.get("DISPLAY"):
        if not env.get("XAUTHORITY"):
            env["XAUTHORITY"] = os.path.expanduser("~/.Xauthority")
        return env

    env["DISPLAY"] = ":0"
    env["XAUTHORITY"] = os.path.expanduser("~/.Xauthority")
    return env


def _preview_log_reader(proc):
    try:
        for line in proc.stdout:
            log_buffer.append(f"[AR_PREVIEW] {line}")
    except Exception:
        return None


@app.route("/api/start_preview", methods=["POST"])
def start_preview():
    global preview_process

    if preview_process is not None and preview_process.poll() is None:
        return jsonify({"success": True, "message": "Already running."})

    my_dir = (
        os.path.dirname(os.path.abspath(__file__))
        if not getattr(sys, "frozen", False)
        else os.path.dirname(sys.executable)
    )
    candidate_dirs = [
        FALLBACK_PROJECT_DIR,
        RUNTIME_BASE_DIR,
        my_dir,
        os.path.join(my_dir, "dist"),
        BASE_DIR,
    ]

    ar_script_path = None
    ar_cwd = None
    for directory in candidate_dirs:
        candidate = os.path.join(directory, "ar_receiver.py")
        if os.path.exists(candidate):
            ar_script_path = candidate
            ar_cwd = directory
            break

    if ar_script_path is None:
        return jsonify(
            {
                "success": False,
                "error": "找不到预览脚本 ar_receiver.py",
            }
        )

    try:
        python_exe = "python" if os.name == "nt" else "python3"
        if getattr(sys, "frozen", False) == False:
            python_exe = sys.executable

        if os.name == "nt":
            env = clean_pyinstaller_env(os.environ.copy())
            preview_process = subprocess.Popen(
                ["cmd.exe", "/k", python_exe, ar_script_path],
                cwd=ar_cwd,
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            active_env = get_active_x11_env()

            if "LD_LIBRARY_PATH" in active_env:
                ld_paths = active_env["LD_LIBRARY_PATH"].split(":")
                ld_paths = [p for p in ld_paths if "/opt/ros" not in p]
                if ld_paths:
                    active_env["LD_LIBRARY_PATH"] = ":".join(ld_paths)
                else:
                    del active_env["LD_LIBRARY_PATH"]

            if "PYTHONPATH" in active_env:
                py_paths = active_env["PYTHONPATH"].split(":")
                py_paths = [p for p in py_paths if "/opt/ros" not in p]
                if py_paths:
                    active_env["PYTHONPATH"] = ":".join(py_paths)
                else:
                    del active_env["PYTHONPATH"]

            infer_wrap_path = os.path.join(ar_cwd, "infer_wrap", "base")
            if os.path.exists(infer_wrap_path):
                current_pythonpath = active_env.get("PYTHONPATH", "")
                active_env["PYTHONPATH"] = (
                    f"{infer_wrap_path}:{current_pythonpath}"
                    if current_pythonpath
                    else infer_wrap_path
                )

            log_buffer.append(f"[AR PREVIEW Launch] python={python_exe}\n")

            ar_log_path = os.path.join(ar_cwd, "ar_preview.log")
            ar_log_file = open(ar_log_path, "w")

            preview_process = subprocess.Popen(
                [python_exe, ar_script_path],
                cwd=ar_cwd,
                env=active_env,
                stdout=ar_log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

            log_buffer.append(
                f"[AR PREVIEW Launch] Process started with PID={preview_process.pid}.\n"
            )

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/stop_preview", methods=["POST"])
def stop_preview():
    global preview_process

    if preview_process is not None and preview_process.poll() is None:
        import signal

        try:
            if os.name == "nt":
                os.kill(preview_process.pid, signal.CTRL_C_EVENT)
            else:
                os.killpg(os.getpgid(preview_process.pid), signal.SIGTERM)

            preview_process.wait(timeout=2)
        except Exception:
            try:
                preview_process.kill()
            except Exception:
                pass

        preview_process = None
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Preview not running"})


sim_pos = [0.0, 0.16, 0.0]
sim_yaw = 0.0
sim_seq = 0


@app.route("/api/sim_control", methods=["POST"])
def sim_control():
    global sim_pos, sim_yaw, sim_seq

    data = request.get_json(silent=True) or {}
    key = data.get("key", "").lower()
    keys = data.get("keys")

    move_speed = 0.05
    turn_speed = 1.0

    active_keys = []
    if isinstance(keys, list):
        active_keys = [
            str(k).lower() for k in keys if str(k).lower() in {"w", "a", "s", "d"}
        ]
    elif key in {"w", "a", "s", "d"}:
        active_keys = [key]

    if active_keys:
        turn_dir = (1 if "d" in active_keys else 0) - (1 if "a" in active_keys else 0)
        move_dir = (1 if "w" in active_keys else 0) - (1 if "s" in active_keys else 0)
        sim_yaw += turn_dir * turn_speed
        rad = math.radians(sim_yaw)
        sim_pos[0] += math.sin(rad) * move_speed * move_dir
        sim_pos[2] += math.cos(rad) * move_speed * move_dir
    elif key in {"set_x", "set_y", "set_z", "set_yaw"}:
        val = data.get("val")
        if val is None:
            return jsonify({"success": False, "error": "Missing val."})
        val = float(val)
        if key == "set_x":
            sim_pos[0] = val
        elif key == "set_y":
            sim_pos[1] = val
        elif key == "set_z":
            sim_pos[2] = val
        elif key == "set_yaw":
            sim_yaw = val
    elif key == "init_xz_yaw":
        sim_pos[0] = 0.0
        sim_pos[2] = 0.0
        sim_yaw = 0.0
    else:
        return jsonify({"success": False, "error": "No key provided."})

    sim_yaw = sim_yaw % 360.0

    payload = {
        "type": "robot_position",
        "pos": sim_pos,
        "euler": [0.0, sim_yaw, 0.0],
        "seq": sim_seq,
        "timestamp": time.time(),
    }

    try:
        config_path = CONFIG_PATH
        target_ip = get_ip()
        target_port = 9005

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                conf = json.load(f)
            target_port = int(conf.get("network", {}).get("control_port", target_port))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = json.dumps(payload).encode("utf-8")
        sock.sendto(msg, (target_ip, target_port))
        sock.close()

        sim_seq += 1

        return jsonify(
            {
                "success": True,
                "pos": sim_pos,
                "yaw": sim_yaw,
                "target": f"{target_ip}:{target_port}",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/match_records", methods=["GET"])
def list_match_records():
    pattern = os.path.join(RUNTIME_BASE_DIR, "match_record_*.json")
    files = _glob.glob(pattern)
    records = []

    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            records.append(
                {
                    "filename": fname,
                    "match_date": data.get("match_date", ""),
                    "total_events": data.get("total_events", 0),
                    "size_bytes": os.path.getsize(fpath),
                }
            )
        except Exception:
            records.append(
                {
                    "filename": fname,
                    "match_date": "",
                    "total_events": -1,
                    "size_bytes": os.path.getsize(fpath),
                }
            )

    records.sort(key=lambda r: r["filename"], reverse=True)
    return jsonify({"success": True, "records": records})


@app.route("/api/match_record/<filename>", methods=["GET"])
def get_match_record(filename):
    if not filename.startswith("match_record_") or not filename.endswith(".json"):
        return jsonify({"success": False, "error": "Invalid filename"}), 400

    fpath = os.path.join(RUNTIME_BASE_DIR, filename)
    if not os.path.isfile(fpath):
        return jsonify({"success": False, "error": "File not found"}), 404

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/match_record/<filename>/download", methods=["GET"])
def download_match_record(filename):
    if not filename.startswith("match_record_") or not filename.endswith(".json"):
        return jsonify({"success": False, "error": "Invalid filename"}), 400

    return send_from_directory(RUNTIME_BASE_DIR, filename, as_attachment=True)


def get_latest_ar_frame():
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8080/ar_feed", timeout=3)
        buffer = b""

        while True:
            chunk = req.read(8192)
            if not chunk:
                return None

            buffer += chunk
            start = buffer.find(b"\xff\xd8")
            end = buffer.find(b"\xff\xd9", start)

            if start != -1 and end != -1:
                return buffer[start : end + 2]
    except Exception as e:
        print("[LLM Test] Failed to capture AR frame: ", e)
        return None


@app.route("/api/test_llm", methods=["POST"])
def test_llm():
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    prompt = data.get("prompt", "描述一下这个画面")

    if not prompt.strip():
        prompt = "描述一下这个画面"

    if not token.strip():
        return jsonify({"error": "请先输入 Access Token"}), 400

    try:
        from openai import OpenAI
    except ImportError:
        return (
            jsonify(
                {"error": "服务器未安装 openai 库, 请在后台执行 pip install openai"}
            ),
            500,
        )

    jpg_data = get_latest_ar_frame()
    if not jpg_data:
        return (
            jsonify(
                {
                    "error": "无法从 127.0.0.1:8080/ar_feed 获取 AR 融合画面，请确认系统已启动。若画面被占用请先关闭预览。"
                }
            ),
            500,
        )

    base64_img = base64.b64encode(jpg_data).decode("utf-8")

    def generate():
        try:
            client = OpenAI(
                api_key=token.strip(),
                base_url="https://aistudio.baidu.com/llm/lmapi/v3",
            )
            chat_completion = client.chat.completions.create(
                model="ernie-4.5-vl-28b-a3b",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_img}"
                                },
                            },
                        ],
                    }
                ],
                stream=True,
                extra_body={"penalty_score": 1, "enable_thinking": True},
                max_completion_tokens=8000,
                temperature=0.2,
                top_p=0.8,
                frequency_penalty=0,
                presence_penalty=0,
            )

            for chunk in chat_completion:
                if not chunk.choices or len(chunk.choices) == 0:
                    continue

                if (
                    hasattr(chunk.choices[0].delta, "reasoning_content")
                    and chunk.choices[0].delta.reasoning_content
                ):
                    content = chunk.choices[0].delta.reasoning_content.replace(
                        "\n", "\\n"
                    )
                    yield f"event: reasoning\ndata: {content}\n\n"
                    continue

                if (
                    hasattr(chunk.choices[0].delta, "content")
                    and chunk.choices[0].delta.content
                ):
                    content = chunk.choices[0].delta.content.replace("\n", "\\n")
                    yield f"event: content\ndata: {content}\n\n"
        except Exception as e:
            err = str(e).replace("\n", "\\n")
            yield f"event: error\ndata: {err}\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    print(f"Starting Setup WebUI on http://{get_ip()}:5000")
    print("Accessible from other computers.")
    app.run(host="0.0.0.0", port=5000)

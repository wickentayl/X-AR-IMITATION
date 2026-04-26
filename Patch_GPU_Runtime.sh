#!/usr/bin/env bash
set -Eeuo pipefail

GL4ES_REPO="${GL4ES_REPO:-https://github.com/ptitSeb/gl4es.git}"
BUILD_ROOT="${BUILD_ROOT:-/tmp/gl4es}"
PREFIX="${PREFIX:-/opt/gl4es}"
MALI_LIB="${MALI_LIB:-/usr/lib/aarch64-linux-gnu/libmali.so.1}"
VERIFY_ONLY=0
SKIP_APT=0
SET_GPU_PERFORMANCE=1

usage() {
  cat <<EOF
Usage: $0 [options]

Build and install the gl4es runtime patch for OrangePi/RK3588 Mali rendering.

Options:
  --verify-only          Only verify renderer and /opt/gl4es files.
  --skip-apt             Do not install apt dependencies.
  --no-gpu-performance   Do not set the Mali devfreq governor to performance.
  --prefix PATH          Install directory. Default: /opt/gl4es
  --build-root PATH      Temporary build directory. Default: /tmp/gl4es
  -h, --help             Show this help.

Environment overrides:
  GL4ES_REPO, BUILD_ROOT, PREFIX, MALI_LIB, DISPLAY, XAUTHORITY
EOF
}

log() {
  printf '[gl4es-patch] %s\n' "$*"
}

die() {
  printf '[gl4es-patch] ERROR: %s\n' "$*" >&2
  exit 1
}

sudo_cmd() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    --skip-apt)
      SKIP_APT=1
      shift
      ;;
    --no-gpu-performance)
      SET_GPU_PERFORMANCE=0
      shift
      ;;
    --prefix)
      [[ $# -ge 2 ]] || die "--prefix requires a path"
      PREFIX="$2"
      shift 2
      ;;
    --build-root)
      [[ $# -ge 2 ]] || die "--build-root requires a path"
      BUILD_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

require_board() {
  local arch
  arch="$(uname -m)"
  case "$arch" in
    aarch64|arm64) ;;
    *) die "this patch is for aarch64/arm64 boards, current arch is $arch" ;;
  esac

  [[ -e /dev/mali0 ]] || die "/dev/mali0 not found"
  [[ -e "$MALI_LIB" ]] || die "Mali userspace library not found: $MALI_LIB"
}

install_deps() {
  if [[ "$SKIP_APT" -eq 1 ]]; then
    log "Skipping apt dependency install"
    return
  fi

  log "Installing build dependencies"
  sudo_cmd apt-get update
  sudo_cmd env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git cmake build-essential libegl-dev libgles-dev mesa-utils
}

fetch_and_patch_gl4es() {
  log "Fetching gl4es into $BUILD_ROOT"
  rm -rf "$BUILD_ROOT"
  git clone --depth 1 "$GL4ES_REPO" "$BUILD_ROOT"

  log "Applying Mali shaderconv patch"
  python3 - "$BUILD_ROOT/src/gl/shaderconv.c" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()

old = '''  const char* GLESUseShaderNonConstantGlobalInitialzers = "#extension GL_EXT_shader_non_constant_global_initializers : enable\\n";
  Tmp = gl4es_inplace_insert(gl4es_getline(Tmp, 1), GLESUseShaderNonConstantGlobalInitialzers, Tmp, &tmpsize);
  ++headline;
'''

new = '''  if(!fpeShader) {
    const char* GLESUseShaderNonConstantGlobalInitialzers = "#extension GL_EXT_shader_non_constant_global_initializers : enable\\n";
    Tmp = gl4es_inplace_insert(gl4es_getline(Tmp, 1), GLESUseShaderNonConstantGlobalInitialzers, Tmp, &tmpsize);
    ++headline;
  }
'''

if new in text:
    print("shaderconv patch already present")
elif old in text:
    path.write_text(text.replace(old, new))
    print("shaderconv patch applied")
else:
    raise SystemExit("shaderconv patch target not found")
PY
}

build_gl4es() {
  log "Building gl4es"
  cmake -S "$BUILD_ROOT" -B "$BUILD_ROOT/build" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DGLX_STUBS=ON \
    -DNOX11=OFF
  cmake --build "$BUILD_ROOT/build" --parallel "$(nproc 2>/dev/null || echo 4)"
}

install_gl4es() {
  local built_lib="$BUILD_ROOT/lib/libGL.so.1"
  [[ -f "$built_lib" ]] || die "built library not found: $built_lib"

  log "Installing gl4es runtime into $PREFIX"
  sudo_cmd mkdir -p "$PREFIX"
  sudo_cmd install -m 0755 "$built_lib" "$PREFIX/libGL.so.1"
  sudo_cmd ln -sfn "$PREFIX/libGL.so.1" "$PREFIX/libGL.so"
  sudo_cmd ln -sfn "$PREFIX/libGL.so.1" "$PREFIX/libGLX.so.0"

  for name in \
    libEGL.so.1 libEGL.so \
    libGLESv2.so.2 libGLESv2.so \
    libGLESv1_CM.so.1 libGLESv1_CM.so
  do
    sudo_cmd ln -sfn "$MALI_LIB" "$PREFIX/$name"
  done
}

set_gpu_performance() {
  [[ "$SET_GPU_PERFORMANCE" -eq 1 ]] || return

  local governor="/sys/devices/platform/fb000000.gpu/devfreq/fb000000.gpu/governor"
  local cur_freq="/sys/devices/platform/fb000000.gpu/devfreq/fb000000.gpu/cur_freq"
  if [[ -e "$governor" ]]; then
    log "Setting GPU governor to performance"
    printf 'performance\n' | sudo_cmd tee "$governor" >/dev/null || true
    [[ -e "$cur_freq" ]] && log "GPU current frequency: $(cat "$cur_freq")"
  else
    log "GPU governor path not found, skipping"
  fi
}

verify_install() {
  [[ -f "$PREFIX/libGL.so.1" ]] || die "$PREFIX/libGL.so.1 not found"
  [[ -L "$PREFIX/libGLX.so.0" ]] || die "$PREFIX/libGLX.so.0 symlink not found"
  [[ -L "$PREFIX/libEGL.so" ]] || die "$PREFIX/libEGL.so symlink not found"

  if ! command -v glxinfo >/dev/null 2>&1; then
    log "glxinfo not found; install mesa-utils or verify by launching app.py"
    return
  fi

  local display="${DISPLAY:-:0}"
  local xauthority="${XAUTHORITY:-$HOME/.Xauthority}"
  log "Checking renderer with DISPLAY=$display"
  local output
  output="$(
    DISPLAY="$display" \
    XAUTHORITY="$xauthority" \
    LD_LIBRARY_PATH="$PREFIX${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    LIBGL_ES=2 \
    glxinfo -B 2>&1 || true
  )"
  printf '%s\n' "$output" | grep -E 'OpenGL vendor|OpenGL renderer|OpenGL version' || true

  if ! printf '%s\n' "$output" | grep -q 'GL4ES using Mali'; then
    die "renderer is not GL4ES using Mali; check X11, libmali, and $PREFIX links"
  fi
}

main() {
  require_board

  if [[ "$VERIFY_ONLY" -eq 0 ]]; then
    install_deps
    fetch_and_patch_gl4es
    build_gl4es
    install_gl4es
    set_gpu_performance
  fi

  verify_install
  log "Done"
}

main "$@"

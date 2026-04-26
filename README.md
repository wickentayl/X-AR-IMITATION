# AR Setup UI

魔改版AR渲染程序，拥有**更高的帧率**和**更低的CPU占用率**。

## PC 使用

PC 可以直接启动整套程序，不依赖香橙派。建议使用 Linux 桌面环境，确保本机有摄像头、OpenGL 显示环境和 Python 3.10+。

```bash
python3 -m pip install -r requirements.txt
python3 -u main.py
```

浏览器打开：

```text
http://127.0.0.1:5000/
```

AR 视频流：

```text
http://127.0.0.1:8080/ar_feed
```

局域网内其他设备访问这台 PC 时，把 `127.0.0.1` 换成 PC 的局域网 IP。

GPU 补丁只用于 OrangePi/RK3588，PC 上不要执行 `Patch_GPU_Runtime.sh`。

## 香橙派使用

首次部署先安装 Python 依赖：

```bash
python3 -m pip install -r requirements.txt
```

首次使用 GPU 渲染前安装 gl4es 补丁：

```bash
bash Patch_GPU_Runtime.sh
```

之后正常启动 WebUI：

```bash
python3 -u main.py
```

启动后在 PC 或香橙派浏览器打开：

```text
http://<board-ip>:5000/
```

## GPU 补丁

首次部署到 OrangePi/RK3588 时执行：

```bash
bash Patch_GPU_Runtime.sh
```

只验证当前环境：

```bash
bash Patch_GPU_Runtime.sh --verify-only
```

不改 GPU governor：

```bash
bash Patch_GPU_Runtime.sh --no-gpu-performance
```

FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel

# The model and corpus are mounted by p1.slurm so that predictions are
# written directly to the host.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential ffmpeg libsm6 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/a2s-requirements.txt
RUN python -m pip install --no-cache-dir pybind11 && \
    python -m pip install --no-cache-dir -r /tmp/a2s-requirements.txt

WORKDIR /workspace/a2s-transformer
CMD ["python", "-u", "predict.py"]

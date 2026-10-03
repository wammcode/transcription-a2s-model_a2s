FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel

#############################################
# Argumentos para UID y GID
ARG USER_ID
ARG GROUP_ID
# Crear el grupo y usuario con los IDs especificados
RUN groupadd -g $GROUP_ID usergroup && \
    useradd -m -u $USER_ID -g $GROUP_ID user && \
    mkdir -p /real-a2s && \
    chown -R user:usergroup /real-a2s && \
    pip install matplotlib
# Establecer el directorio de trabajo
#WORKDIR /workspace
#############################################

COPY . /a2s-transformer
WORKDIR /a2s-transformer

RUN apt update --fix-missing
RUN apt install build-essential -y
RUN apt install ffmpeg libsm6 -y
RUN apt install vim -y
RUN apt clean
RUN pip install --upgrade pip
RUN pip install pybind11
RUN pip install --no-cache-dir -r requirements.txt

#CMD ["ls"]
CMD ["bash", "run.sh"]
#CMD ["pwd"]


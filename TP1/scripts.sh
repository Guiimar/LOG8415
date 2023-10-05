#!/bin/bash
git clone https://github.com/Guiimar/LOG8415.git
cd LOG8415/TP1
docker build -t log8415 .
docker run -it log8415

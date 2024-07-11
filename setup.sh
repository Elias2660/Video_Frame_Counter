#!/bin/bash

mv *.py ../
mv libopenh264-1.6.0-linux64.3.so ../

pip install opencv-python-headless

wget https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.gz
tar xzvf x264-master.tar.gz

wget https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.gz
tar xzvf nasm-2.15.05.tar.gz
cd nasm-2.15.05

./configure --prefix="$HOME/nasm_build"
make
make install

cd ..

cd x264-master
./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static --disable-asm
make
make install
export PATH="$HOME/bin:$PATH"

nasm -v

cd ..

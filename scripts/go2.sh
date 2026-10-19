cd /home/claude/watch
python3 render2.py 0 > q0.log 2>&1 &
python3 render2.py 1 > q1.log 2>&1 &
wait
ls seg2/*.mp4 | grep -v tmp | sed "s/^/file '/;s/$/'/" > l2.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i l2.txt -i aw2n.wav -c:v libx264 -preset fast -crf 21 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart relogio_3d_24s_9x16.mp4
echo done > done2.txt

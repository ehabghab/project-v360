for set=1
    for vid=[1,2,3,4,5,7,8]
        mkdir(['videos/',num2str(set),'/',num2str(vid)]);
        qp = 15; % 产生原始chunk
        command =['ffmpeg -r 30 -i ',sprintf('videos\\%d\\%03d.mp4',set,vid), ...
            ' -an -c:v libx264 -qp ',num2str(qp),' -g 30 -vf fps=30 -f segment ', ...
            '-segment_list videos/',num2str(set),'/',num2str(vid),'/tmp.m3u8 -segment_time 1 ', ...
            'videos/',num2str(set),'/',num2str(vid),'/%03d.mp4'];
        system(command)
    end
end
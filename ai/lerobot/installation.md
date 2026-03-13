conda create -y -n lerobot python=3.12
conda activate lerobot
conda install ffmpeg -c conda-forge # 영상, 오디오를 읽고, 변환하고, 인코딩하는 도구
# 오류 발생
librsvg: The post-link script did not complete.
To take advantage of gdk-pixbuf's support for librsvg, please run:
    C:\Users\yuyou\miniconda3\envs\lerobot\Scripts\.gdk-pixbuf-post-link.bat

done
ERROR conda.core.link:_execute(1026): An error occurred while installing package 'conda-forge::gdk-pixbuf-2.44.5-h1f5b9c4_0'.
Rolling back transaction: done

UnicodeDecodeError('cp949', b"g_module_open() failed for C:\\Users\\yuyou\\miniconda3\\envs\\lerobot\\Library\\lib\\gdk-pixbuf-2.0\\2.10.0\\loaders\\libpixbufloader_svg.dll: 'C:\\Users\\yuyou)
()
# 리눅스 환경에서 다시 시도
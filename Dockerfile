# 使用nginx作为基础镜像  
FROM nginx  
  
# 将本地文件复制到容器的/usr/share/nginx/html/目录下  
COPY tools /usr/share/nginx/html/tools  
COPY docs /usr/share/nginx/html/docs  
COPY install /usr/share/nginx/html/install  
COPY install.py /usr/share/nginx/html/install.py  
  
# 暴露容器的80端口到主机的8080端口  
EXPOSE 80  
  
# 启动nginx服务  
CMD ["nginx", "-g", "daemon off;"]
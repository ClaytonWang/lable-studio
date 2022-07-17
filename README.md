
## 开发文档

[多语言](docs/develop/i18n.md)

#### 模型在服务器上的位置目录

``` bash

/label-model-${ENV:-dev}

```

#### 导入导出数据在服务器上的位置目录

``` bash

/label-data-${ENV:-dev}

```

#### 环境启动方式

``` bash

#root 
cd ~/${ENV:-dev}/${ENV:-dev}-env && docker-compose pull && docker-compose down && docker-compose up -d

```

#### 查看Debug logs

``` bash

#root 
cd ~/${ENV:-dev}/${ENV:-dev}-env && docker-compose logs

#或者
docker container logs container_name

```

#### Docker Image
```

https://git.digitalbrain.cn/engineering-group/label-studio/pkgs/container/label-studio

```

# 本次需要 需求说明书自动生成工具

1. 项目技术栈 基于electron,react,typescript 开发,后端需要用到fastapi
工作逻辑是 electron 桌面app 点击上传 input.excel ，python 后端会解析excel，并调用ai 生成相应的数据，然后python使用 python-docx 写入文件到一个输出的output.word 文档中。electron 前端需要使用mermaid-cli库 解析python 后端的mermaid时序图，写入到output.word 中，其中需要前后端合作,请你基于此设计开发步骤。我将在下一步具体说明解析步骤和生成步骤，现在先设计架构

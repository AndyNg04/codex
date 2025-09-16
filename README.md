# Todo List 网页应用

这是一个基于 Flask 构建的待办事项（Todo List）网页应用，提供现代化的浏览器界面，用于集中管理任务。应用支持新增、搜索、筛选、编辑、标记完成以及删除任务，所有数据会以 JSON 文件的形式保存在当前用户主目录中。

## 功能概览

- ✏️ **添加任务**：填写标题、描述与截止日期（YYYY-MM-DD），快速创建待办事项。
- 🔍 **搜索与筛选**：按关键词检索任务，并在「全部 / 进行中 / 已完成」之间切换视图。
- ✅ **状态管理**：一键将任务标记为完成或恢复为进行中。
- 🪄 **即时编辑**：在右侧面板查看并修改任务详情，支持同步调整状态。
- 📅 **超期提示**：对已过截止日期且未完成的任务进行醒目标记。
- 💾 **本地持久化**：任务信息默认保存在 `~/.todo_app_data.json`，应用启动时自动加载。

## 快速开始

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **启动开发服务器**

   ```bash
   python -m todo_app
   ```

   默认会在 <http://127.0.0.1:5000> 启动一个开发服务器，打开浏览器即可访问。首次运行时会在用户主目录下创建 `~/.todo_app_data.json` 用于存储任务数据。

### 可选配置

服务器启动时支持以下环境变量：

| 变量名              | 说明                                   | 默认值       |
| ------------------- | -------------------------------------- | ------------ |
| `TODO_APP_HOST`     | 监听地址                               | `127.0.0.1` |
| `TODO_APP_PORT`     | 监听端口                               | `5000`      |
| `TODO_APP_DEBUG`    | 设置为 `1` 可开启 Flask 调试模式        | 关闭        |
| `TODO_APP_SECRET_KEY` | Flask 会话秘钥（用于 flash 消息等） | `todo-app-secret` |

示例：

```bash
TODO_APP_HOST=0.0.0.0 TODO_APP_PORT=8080 python -m todo_app
```

## 项目结构

```
.
├── README.md
├── requirements.txt
└── todo_app
    ├── __init__.py
    ├── __main__.py
    ├── app.py
    ├── models.py
    ├── storage.py
    └── templates
        ├── base.html
        └── index.html
```

- `todo_app/models.py`：任务数据模型定义，负责序列化和状态属性。
- `todo_app/storage.py`：本地 JSON 存储工具，负责读取与保存任务列表。
- `todo_app/app.py`：Flask 应用入口，包含所有路由与表单逻辑。
- `todo_app/templates/`：Jinja2 模板，提供响应式的网页界面。

欢迎在此基础上扩展更多功能，例如任务标签、提醒、团队协作等。若需要部署到生产环境，可在 WSGI/ASGI 服务器上运行 `todo_app.app:create_app`。

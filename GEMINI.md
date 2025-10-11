# GEMINI.md

## Project Overview

This project is a web application with a monorepo structure. It consists of a frontend and a backend.

- **Frontend:** The frontend is a [Vue Vben Admin](https://github.com/vbenjs/vue-vben-admin) template, which is a Vue 3, Vite, and TypeScript project. It uses `pnpm` for package management and `turbo` for monorepo management.
- **Backend:** The backend is a Python project using the [FastAPI](https://fastapi.tiangolo.com/) framework. It provides a RESTful API for the frontend. It uses `uv` for package management and `hatch` for building.

## Building and Running

### Frontend

To build and run the frontend, you need to have `pnpm` and `Node.js` installed.

1. **Install dependencies:**

   ```bash
   cd frontend
   pnpm install
   ```
2. **Run in development mode:**

   ```bash
   pnpm run dev:antd
   ```
3. **Build for production:**

   ```bash
   pnpm run build
   ```

### Backend

To build and run the backend, you need to have `uv` and `Python >= 3.9` installed.

1. **Install dependencies:**

   ```bash
   cd backend
   uv sync
   ```
2. **Run in development mode:**

   ```bash
   uv run main.py
   ```
3. **Build for production:**

   ```bash
   uv run build.py
   ```

## Development Conventions

### Frontend

The frontend follows the conventions of the `vue-vben-admin` template. Please refer to its [documentation](https://doc.vben.pro/) for more details.

- **Commit Messages:** The project uses [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. A `commitlint` configuration is included in the `frontend` directory.
- **Linting:** The project uses `ESLint` and `Prettier` for code linting and formatting.
- **Testing:** The project uses `vitest` for unit testing and `playwright` for end-to-end testing.

### Backend

The backend follows standard Python development practices.

- **Dependency Management:** The project uses `uv` to manage dependencies. Dependencies are listed in the `pyproject.toml` file.
- **Code Style:** The project does not have a strict code style guide, but it is recommended to follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).

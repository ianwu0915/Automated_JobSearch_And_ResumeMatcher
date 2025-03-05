# Job Match App

A React-based job matching application built with TypeScript and Vite.

## Tech Stack

- React + TypeScript
- Vite
- Tailwind CSS
- Additional Libraries:
  - react-router-dom (Routing)
  - axios (API calls)
  - formik (Form handling)
  - yup (Form validation)
  - @headlessui/react (UI components)
  - @heroicons/react (Icons)

## Setup Instructions

### Prerequisites

1. Install NVM (Node Version Manager):

```bash
# Using curl
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Or using wget
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```

2. Add the following to your shell configuration file (`~/.zshrc` or `~/.bashrc`):

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
```

3. Reload your shell configuration and install Node.js:

```bash
source ~/.zshrc  # or source ~/.bashrc
nvm install 22.9.0
nvm use 22.9.0
```

### Project Setup

1. Create a new Vite project:

```bash
npm create vite@latest job-match-app -- --template react-ts
```

2. Navigate to the project directory:

```bash
cd job-match-app
```

3. Install main dependencies:

```bash
npm install react-router-dom axios formik yup @headlessui/react @heroicons/react
```

4. Set up Tailwind CSS:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Development

### Available Plugins

Currently, two official Vite plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) (uses Babel)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) (uses SWC)

### ESLint Configuration

For production applications, enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    ...tseslint.configs.recommendedTypeChecked,
    // Or for stricter rules:
    // ...tseslint.configs.strictTypeChecked,
    // For stylistic rules:
    // ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    parserOptions: {
      project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

#### Additional React-specific Lint Rules

Install and configure React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default tseslint.config({
  plugins: {
    "react-x": reactX,
    "react-dom": reactDom,
  },
  rules: {
    ...reactX.configs["recommended-typescript"].rules,
    ...reactDom.configs.recommended.rules,
  },
});
```

## Configuration

### Vite Configuration

The `vite.config.ts` file contains important project settings:

```typescript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),  // Enables '@' imports from src directory
  },
},
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',      // Points to Django backend
      changeOrigin: true,
      secure: false,
    },
  },
}
```

#### Path Aliases

- Use `@` to import from the `src` directory
- Example: `import Button from '@/components/Button'` instead of `'../../components/Button'`

#### Development Server

- Frontend runs on default port `5173` (http://localhost:5173)
- API requests to `/api/*` are automatically proxied to Django backend (port 8000)
- Helps avoid CORS issues during development

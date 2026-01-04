# PROJECT HANDOFF: Dual AI Studio

**Company:** Recursive Fractal Systems (RFS)

## Overview

This document serves as a comprehensive handoff guide for the Dual AI Studio project, providing all necessary information for future development, maintenance, and understanding of the codebase.

## Project Description

Dual AI Studio is an innovative creative platform that integrates multiple AI assistants (Claude and ChatGPT) working collaboratively within a unified workspace. The studio provides tools for 3D modeling, audio production, game development, and creative content generation.

## Core Features

### 1. Dual AI Integration
- Simultaneous interaction with Claude (Anthropic) and ChatGPT (OpenAI)
- Split-pane interface for side-by-side AI responses
- Unified conversation history
- Context sharing between AI assistants

### 2. Creative Tools Integration
- **Blender Integration**: 3D modeling and animation
- **Godot Engine**: Game development environment
- **LMMS**: Music and audio production
- **Image Generation**: AI-powered visual content creation

### 3. Project Management
- Multi-project workspace
- Version control integration
- File organization and management
- Export and sharing capabilities

## Technical Architecture

### Frontend
- **Framework**: Electron + React
- **UI Library**: Material-UI (MUI)
- **State Management**: React Context API
- **Styling**: Emotion (CSS-in-JS)

### Backend
- **Runtime**: Node.js
- **API Integration**: 
  - Anthropic Claude API
  - OpenAI GPT API
- **File System**: Electron's native file system APIs

### Key Dependencies
```json
{
  "electron": "^28.0.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "@mui/material": "^5.15.0",
  "@emotion/react": "^11.11.0",
  "@emotion/styled": "^11.11.0",
  "axios": "^1.6.0"
}
```

## Directory Structure

```
dual-ai-studio/
├── src/
│   ├── main/           # Electron main process
│   ├── renderer/       # React application
│   │   ├── components/ # React components
│   │   ├── contexts/   # Context providers
│   │   ├── hooks/      # Custom React hooks
│   │   └── utils/      # Utility functions
│   └── shared/         # Shared code between processes
├── public/             # Static assets
├── build/              # Build output
└── package.json        # Project dependencies
```

## Key Files and Their Purposes

### Main Process Files
- `src/main/main.js` - Electron main process entry point
- `src/main/preload.js` - Preload script for secure IPC
- `src/main/api/` - API integration handlers

### Renderer Process Files
- `src/renderer/App.jsx` - Main React application component
- `src/renderer/components/AIPanel.jsx` - Dual AI interface
- `src/renderer/components/ToolsPanel.jsx` - Creative tools integration
- `src/renderer/contexts/ProjectContext.jsx` - Project state management

## API Integration

### Claude API
- Endpoint: `https://api.anthropic.com/v1/messages`
- Authentication: API key via headers
- Model: claude-3-opus-20240229 (or latest)

### OpenAI API
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Authentication: Bearer token
- Model: gpt-4 (or latest)

## Configuration

### Environment Variables
```
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
```

### User Settings
Stored in: `~/.dual-ai-studio/config.json`
- API keys (encrypted)
- User preferences
- Recent projects
- Tool paths

## Development Setup

1. **Clone Repository**
   ```bash
   git clone [repository-url]
   cd dual-ai-studio
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Set Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your API keys

4. **Run Development Server**
   ```bash
   npm run dev
   ```

5. **Build Application**
   ```bash
   npm run build
   ```

## Testing

- **Unit Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright
- **Run Tests**: `npm test`

## Known Issues and Considerations

1. **API Rate Limits**: Both Claude and ChatGPT have rate limits
2. **Large File Handling**: Consider chunking for large 3D models
3. **Cross-Platform**: Ensure tool paths work across OS
4. **Security**: API keys must be securely stored

## Future Enhancements

1. **Real-time Collaboration**: Multi-user project editing
2. **Plugin System**: Extensible architecture for custom tools
3. **Cloud Sync**: Project backup and synchronization
4. **Advanced AI Features**: Fine-tuned models for specific creative tasks
5. **Performance Optimization**: Lazy loading and code splitting

## Deployment

### Building for Production
```bash
npm run build:win   # Windows
npm run build:mac   # macOS
npm run build:linux # Linux
```

### Distribution
- Package using Electron Builder
- Code signing required for macOS and Windows
- Consider auto-update implementation

## Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor API changes from Anthropic and OpenAI
- Update Electron for security patches

### Monitoring
- Error logging and reporting
- Usage analytics (optional, with user consent)
- Performance metrics

## Support and Documentation

- **User Guide**: See `docs/user-guide.md`
- **API Documentation**: See `docs/api.md`
- **Contributing**: See `CONTRIBUTING.md`

## Attribution

**Company**: Recursive Fractal Systems (RFS)  
**Creator**: Adam Lee Hatchett  
**Location**: Hampton, Virginia, USA  
**Copyright**: © 2026 Adam Lee Hatchett / Recursive Fractal Systems (RFS)  
**Date**: January 2026  
**License**: Proprietary (pending license selection)

All code, architecture, and innovative features were created by Adam Lee Hatchett under Recursive Fractal Systems (RFS).

**Note**: Third-party open-source tools (Blender, Godot, LMMS, etc.) are NOT included and must be downloaded separately according to their respective licenses.

## Contact

For questions or issues regarding this handoff, please contact the development team or refer to the project documentation.

---

**Last Updated**: January 2026

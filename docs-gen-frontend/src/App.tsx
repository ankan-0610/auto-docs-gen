// src/App.tsx
import React, { useState } from 'react';
import { Box, Button, Typography, TextField, IconButton, MenuItem,Select, SelectChangeEvent, FormControl, InputLabel } from '@mui/material';
import Editor from '@monaco-editor/react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import axios from 'axios';
import DocumentationDisplay from './DocDisplay';

const App: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [repoLink, setRepoLink] = useState<string>('');
  const [documentation, setDocumentation] = useState<string>('');
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  const [language, setLanguage] = useState<string>('javascript'); // Default language is JavaScript

  // Define light and dark themes using MUI's createTheme
  const lightTheme = createTheme({
    palette: {
      mode: 'light',
      background: {
        default: '#f5f5f5', // Light background color
      },
    },
  });

  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      background: {
        default: '#121212', // Dark background color
      },
    },
  });

  const handleCodeChange = (newValue: string | undefined) => {
    setCode(newValue || '');
  };

  const handleGenerateDocs = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/generate-docs', {
        code: code || undefined,
        repoLink: repoLink || undefined,
      });
      setDocumentation(response.data.documentation);
    } catch (error) {
      console.error('Error generating docs:', error);
    }
  };

  const toggleTheme = () => {
    setThemeMode((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const handleLanguageChange = (event: SelectChangeEvent<string>) => {
    setLanguage(event.target.value as string);
  };

  return (
    <ThemeProvider theme={themeMode === 'light' ? lightTheme : darkTheme}>
      {/* Dynamically apply background color based on theme */}
      <Box
        sx={{
          backgroundColor: themeMode === 'light' ? '#f5f5f5' : '#121212',
          minHeight: '100vh', // Full viewport height
          padding: '1rem',
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" className="text-center">
            Code Documentation Generator
          </Typography>

          {/* Theme Toggle Button */}
          <IconButton onClick={toggleTheme}>
            {themeMode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
          </IconButton>
        </Box>

        <Box className="space-y-2">
          <TextField
            label="Repository Link"
            fullWidth
            value={repoLink}
            onChange={(e) => setRepoLink(e.target.value)}
            variant="outlined"
          />

          <Typography variant="body1">Or paste your code below:</Typography>

          {/* Language Selector */}
          <FormControl fullWidth variant="outlined" margin="normal">
            <InputLabel id="language-select-label">Language</InputLabel>
            <Select
              labelId="language-select-label"
              id="language-select"
              value={language}
              onChange={handleLanguageChange}
              label="Language"
            >
              <MenuItem value="javascript">JavaScript</MenuItem>
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="cpp">C++</MenuItem>
              <MenuItem value="c">C</MenuItem>
              <MenuItem value="java">Java</MenuItem>
              <MenuItem value="go">Golang</MenuItem>
              <MenuItem value="rust">Rust</MenuItem>
              <MenuItem value="typescript">TypeScript</MenuItem>
            </Select>
          </FormControl>

          <Editor
            height="300px"
            language={language} // Dynamically set the language based on user selection
            value={code}
            onChange={handleCodeChange}
            theme={themeMode === 'light' ? 'light' : 'vs-dark'}
          />

          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateDocs}
            className="w-full"
          >
            Generate Documentation
          </Button>
        </Box>

        {documentation && (
          // <Box className="mt-4 p-4 border rounded">
          //   <Typography variant="h6">Generated Documentation:</Typography>
          //   <Typography variant="body2">{documentation}</Typography>
          // </Box>
          <DocumentationDisplay docs={ documentation } />
        )}
      </Box>
    </ThemeProvider>
  );
};

export default App;
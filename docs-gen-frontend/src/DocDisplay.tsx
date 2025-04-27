import React from 'react';
import { Box, Typography } from '@mui/material';
import ReactMarkdown from 'react-markdown';

const DocumentationDisplay: React.FC<{ docs: string }> = ({ docs }) => {
  return (
    <Box className="mt-4 p-4 border rounded bg-white dark:bg-gray-800">
      <Typography variant="h6" gutterBottom>
        Generated Documentation:
      </Typography>
      <ReactMarkdown>
        {docs}
      </ReactMarkdown>
    </Box>
  );
};

export default DocumentationDisplay;

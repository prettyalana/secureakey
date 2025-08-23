import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface Props {
  repoName: string;
  filePath: string;
  authToken: string;
  onClose: () => void;
}

export default function FileEditor({ repoName, filePath, authToken, onClose }: Props) {
  const [content, setContent] = useState('');
  const [sha, setSha] = useState('');

  useEffect(() => {
    fetch(`https://secureakey-backend.onrender.com/file/${repoName}/${filePath}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
      setContent(data.content);
      setSha(data.sha);
    });
  }, []);

  const save = async () => {
    await fetch(`https://secureakey-backend.onrender.com/file/${repoName}/${filePath}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${authToken}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_content: content, sha: sha })
    });
    alert('Saved!');
    onClose();
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)' }}>
      <div style={{ background: 'white', margin: '2rem', height: 'calc(100vh - 4rem)' }}>
        <div style={{ padding: '1rem', background: '#ff1493', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <span>{filePath}</span>
          </div>
          <div>
            <button onClick={save} style={{ float: 'right', marginLeft: '1rem' }}>Save</button>
            <button onClick={onClose} style={{ float: 'right' }}>Close</button>
          </div>
        </div>
        <Editor height="90%" value={content} onChange={(val) => setContent(val || '')} />
      </div>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Card, CardContent, Grid, Paper, Chip } from '@mui/material';
import { PlayArrow, Stop, VideocamOff, CameraAlt } from '@mui/icons-material';
import axios from 'axios';

export default function CameraPage() {
  const [running, setRunning] = useState(false);
  const apiUrl = import.meta.env.VITE_CAMERA_API_URL || 'http://localhost:8001/api';

  const checkStatus = async () => {
    try {
      const res = await axios.get(`${apiUrl}/camera/status`);
      setRunning(res.data.running);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    await axios.post(`${apiUrl}/camera/start`);
    checkStatus();
  };

  const handleStop = async () => {
    await axios.post(`${apiUrl}/camera/stop`);
    checkStatus();
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CameraAlt fontSize="large" color="primary" /> Camera AI & Thị giác máy tính
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Hệ thống nhận diện sử dụng YOLOv8 để đếm số lượng sinh viên trong phòng.
          </Typography>
        </Box>
        <Chip 
          label={running ? "Đang hoạt động" : "Ngoại tuyến"} 
          color={running ? "success" : "default"} 
          variant="outlined" 
          sx={{ fontWeight: 'bold' }} 
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 2, 
              border: '1px solid #e2e8f0', 
              borderRadius: 3,
              bgcolor: running ? '#000' : '#f8fafc',
              minHeight: 480,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              overflow: 'hidden'
            }}
          >
            {running ? (
              <img 
                src={`${apiUrl}/camera/stream`} 
                alt="AI Camera Stream" 
                style={{ width: '100%', height: 'auto', borderRadius: '8px' }} 
              />
            ) : (
              <Box sx={{ textAlign: 'center', color: '#94a3b8' }}>
                <VideocamOff sx={{ fontSize: 64, mb: 2 }} />
                <Typography variant="h6">Camera chưa được bật</Typography>
                <Typography variant="body2">Vui lòng khởi động Camera ở bảng điều khiển bên cạnh</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, border: '1px solid #e2e8f0', boxShadow: 'none' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Bảng điều khiển
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Việc xử lý hình ảnh AI tốn khá nhiều tài nguyên hệ thống. Hãy tắt camera khi không sử dụng.
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  size="large"
                  startIcon={<PlayArrow />}
                  onClick={handleStart} 
                  disabled={running} 
                  fullWidth
                >
                  Khởi động Camera
                </Button>
                <Button 
                  variant="outlined" 
                  color="error" 
                  size="large"
                  startIcon={<Stop />}
                  onClick={handleStop} 
                  disabled={!running}
                  fullWidth
                >
                  Dừng xử lý
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

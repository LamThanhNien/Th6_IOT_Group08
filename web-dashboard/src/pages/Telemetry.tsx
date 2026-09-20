import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import api from '../services/api';

export default function TelemetryPage() {
  const [telemetry, setTelemetry] = useState<any[]>([]);

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const res = await api.get('/telemetry/history?limit=50');
        setTelemetry(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Lịch sử Dữ liệu Cảm biến</Typography>
      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3, maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f8fafc' }}>Thời gian</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f8fafc' }}>Thiết bị</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f8fafc' }}>Phòng</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f8fafc' }}>Nhiệt độ (°C)</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f8fafc' }}>Độ ẩm (%)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {telemetry.map((t, index) => (
              <TableRow key={index}>
                <TableCell>{new Date(t.timestamp).toLocaleString()}</TableCell>
                <TableCell>{t.device_id}</TableCell>
                <TableCell>{t.room_id}</TableCell>
                <TableCell>{t.temperature}</TableCell>
                <TableCell>{t.humidity}</TableCell>
              </TableRow>
            ))}
            {telemetry.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">Chưa có dữ liệu cảm biến</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

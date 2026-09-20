import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip } from '@mui/material';
import api from '../services/api';

export default function DevicesPage() {
  const [devices, setDevices] = useState<any[]>([]);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const res = await api.get('/devices/');
        setDevices(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchDevices();
    const interval = setInterval(fetchDevices, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Quản lý Thiết bị IoT</Typography>
      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Mã thiết bị</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Tên thiết bị</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Phòng</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Loại thiết bị</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Trạng thái</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Lần cuối online</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {devices.map((device) => (
              <TableRow key={device.device_id}>
                <TableCell>{device.device_id}</TableCell>
                <TableCell>{device.device_name}</TableCell>
                <TableCell>{device.room_id}</TableCell>
                <TableCell>{device.device_type}</TableCell>
                <TableCell>
                  <Chip 
                    label={device.online ? 'Online' : 'Offline'} 
                    color={device.online ? 'success' : 'error'} 
                    size="small"
                  />
                </TableCell>
                <TableCell>{device.last_seen ? new Date(device.last_seen).toLocaleString() : 'N/A'}</TableCell>
              </TableRow>
            ))}
            {devices.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">Chưa có thiết bị nào</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

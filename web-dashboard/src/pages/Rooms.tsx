import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip } from '@mui/material';
import api from '../services/api';

export default function RoomsPage() {
  const [rooms, setRooms] = useState<any[]>([]);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const res = await api.get('/rooms/');
        setRooms(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchRooms();
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Quản lý Phòng học</Typography>
      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Mã phòng</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Tên phòng</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Sức chứa</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Ngưỡng cảnh báo nhiệt độ</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rooms.map((room) => (
              <TableRow key={room.room_code}>
                <TableCell><Chip label={room.room_code} color="primary" variant="outlined" /></TableCell>
                <TableCell>{room.room_name}</TableCell>
                <TableCell>{room.occupancy_limit} sinh viên</TableCell>
                <TableCell>{room.temperature_threshold}°C</TableCell>
              </TableRow>
            ))}
            {rooms.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center">Chưa có dữ liệu phòng học</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

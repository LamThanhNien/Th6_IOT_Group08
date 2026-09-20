import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, Button } from '@mui/material';
import api from '../services/api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/alerts/');
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const acknowledgeAlert = async (alertId: number) => {
    try {
      await api.patch(`/alerts/${alertId}/acknowledge`);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'Error': return 'error';
      case 'Warning': return 'warning';
      case 'Info': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Cảnh báo Hệ thống (Rule Engine)</Typography>
      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 3 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Thời gian</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Phòng</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Nguồn phát</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Mức độ</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Tiêu đề</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Nội dung</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Trạng thái</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.map((alert) => (
              <TableRow key={alert.id} sx={{ bgcolor: alert.acknowledged ? 'transparent' : '#fff1f2' }}>
                <TableCell>{new Date(alert.created_at).toLocaleString()}</TableCell>
                <TableCell>{alert.room_id}</TableCell>
                <TableCell>{alert.source_id}</TableCell>
                <TableCell>
                  <Chip label={alert.severity} color={getSeverityColor(alert.severity)} size="small" />
                </TableCell>
                <TableCell fontWeight="bold">{alert.title}</TableCell>
                <TableCell>{alert.message}</TableCell>
                <TableCell>
                  {alert.acknowledged ? (
                    <Typography variant="body2" color="text.secondary">Đã xác nhận</Typography>
                  ) : (
                    <Button variant="contained" color="primary" size="small" onClick={() => acknowledgeAlert(alert.id)}>
                      Xác nhận
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {alerts.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">Chưa có cảnh báo nào</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

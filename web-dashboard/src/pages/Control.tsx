import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, Switch, FormControlLabel, Grid, CircularProgress, Button } from '@mui/material';
import { FlashOn, WbIncandescent, WindPower } from '@mui/icons-material';
import api from '../services/api';

export default function ControlPage() {
  const [devices, setDevices] = useState<any[]>([]);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

  const fetchDevices = async () => {
    try {
      const res = await api.get('/devices/');
      setDevices(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  const sendCommand = async (deviceId: string, roomId: string, action: string, value: any) => {
    setLoading(prev => ({ ...prev, [`${deviceId}_${action}`]: true }));
    try {
      await api.post('/commands/', {
        device_id: deviceId,
        room_id: roomId,
        action: action,
        value: value
      });
      // Give the simulator some time to process
      setTimeout(fetchDevices, 1000);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(prev => ({ ...prev, [`${deviceId}_${action}`]: false }));
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Điều khiển Thiết bị</Typography>
      
      <Grid container spacing={3}>
        {devices.filter(d => d.device_type === 'esp32_controller' || d.device_type === 'Simulator' || d.device_type?.toLowerCase().includes('esp32')).map((device) => (
          <Grid item xs={12} md={6} lg={4} key={device.device_id}>
            <Card sx={{ border: '1px solid #e2e8f0', borderRadius: 3, boxShadow: 'none' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <FlashOn color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    {device.device_name}
                  </Typography>
                </Box>
                <Typography color="text.secondary" gutterBottom>Phòng: {device.room_id}</Typography>
                <Typography color="text.secondary" sx={{ mb: 3 }}>
                  Trạng thái: {device.online ? 'Online' : 'Offline'}
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <WbIncandescent sx={{ mr: 2, color: device.led_status ? '#f59e0b' : '#94a3b8' }} />
                      <Typography fontWeight="500">Đèn LED</Typography>
                    </Box>
                    {loading[`${device.device_id}_SET_LED`] ? (
                      <CircularProgress size={24} />
                    ) : (
                      <Switch 
                        checked={device.led_status}
                        onChange={(e) => sendCommand(device.device_id, device.room_id, 'SET_LED', e.target.checked)}
                        disabled={!device.online}
                        color="primary"
                      />
                    )}
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <WindPower sx={{ mr: 2, color: device.fan_status ? '#3b82f6' : '#94a3b8' }} />
                      <Typography fontWeight="500">Quạt (Fan)</Typography>
                    </Box>
                    {loading[`${device.device_id}_SET_FAN`] ? (
                      <CircularProgress size={24} />
                    ) : (
                      <Switch 
                        checked={device.fan_status}
                        onChange={(e) => sendCommand(device.device_id, device.room_id, 'SET_FAN', e.target.checked)}
                        disabled={!device.online}
                        color="primary"
                      />
                    )}
                  </Box>
                </Box>

                <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #e2e8f0' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Testing Simulator (Giả lập tăng nhiệt độ):
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => sendCommand(device.device_id, device.room_id, 'ENABLE_HIGH_TEMP', true)}
                    sx={{ mr: 1 }}
                  >
                    Bật High Temp
                  </Button>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    color="secondary"
                    onClick={() => sendCommand(device.device_id, device.room_id, 'ENABLE_HIGH_TEMP', false)}
                  >
                    Tắt High Temp
                  </Button>
                </Box>

              </CardContent>
            </Card>
          </Grid>
        ))}
        {devices.length === 0 && (
          <Grid item xs={12}>
            <Typography>Chưa có thiết bị nào để điều khiển.</Typography>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

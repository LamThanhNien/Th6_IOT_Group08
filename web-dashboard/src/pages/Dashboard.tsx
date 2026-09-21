import React, { useEffect, useState } from 'react';
import { Grid, Card, CardContent, Typography, Box, Avatar, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { DeviceThermostat, WaterDrop, Groups, CheckCircle, WarningAmber, Notifications } from '@mui/icons-material';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import api from '../services/api';

export default function DashboardPage() {
  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [vision, setVision] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tRes, vRes, histRes, alertsRes] = await Promise.allSettled([
          api.get('/telemetry/latest'),
          api.get('/vision/latest'),
          api.get('/telemetry/history?limit=10'),
          api.get('/alerts/?limit=5')
        ]);

        if (tRes.status === 'fulfilled' && Array.isArray(tRes.value.data)) {
          setTelemetry(tRes.value.data);
        }
        if (vRes.status === 'fulfilled' && Array.isArray(vRes.value.data)) {
          setVision(vRes.value.data);
        }
        if (histRes.status === 'fulfilled' && Array.isArray(histRes.value.data)) {
          setHistory([...histRes.value.data].reverse());
        }
        if (alertsRes.status === 'fulfilled' && Array.isArray(alertsRes.value.data)) {
          setAlerts(alertsRes.value.data.slice(0, 5));
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const temp = telemetry.length > 0 ? telemetry[0].temperature : '--';
  const hum = telemetry.length > 0 ? telemetry[0].humidity : '--';
  const person = vision.length > 0 ? vision[0].person_count : '--';
  
  const hasUnackAlert = alerts.some(a => !a.acknowledged);

  const stats = [
    { title: 'Nhiệt độ', value: `${temp}°C`, icon: <DeviceThermostat />, color: '#ef4444', bg: '#fee2e2' },
    { title: 'Độ ẩm', value: `${hum}%`, icon: <WaterDrop />, color: '#3b82f6', bg: '#dbeafe' },
    { title: 'Số sinh viên', value: person, icon: <Groups />, color: '#8b5cf6', bg: '#ede9fe' },
    { 
      title: 'Trạng thái', 
      value: hasUnackAlert ? 'Có Cảnh Báo' : 'Bình thường', 
      icon: hasUnackAlert ? <WarningAmber /> : <CheckCircle />, 
      color: hasUnackAlert ? '#f59e0b' : '#10b981', 
      bg: hasUnackAlert ? '#fef3c7' : '#d1fae5' 
    },
  ];

  // Format data for Recharts
  const chartData = history.map(h => ({
    time: new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    temp: h.temperature,
    hum: h.humidity
  }));

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="600" color="primary.main">Tổng quan Hệ thống</Typography>
        <Typography variant="body1" color="text.secondary">
          Giám sát môi trường và số lượng người trong thời gian thực.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {stats.map((stat, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 'none' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', p: 3 }}>
                <Avatar sx={{ bgcolor: stat.bg, color: stat.color, width: 56, height: 56, mr: 2 }}>
                  {stat.icon}
                </Avatar>
                <Box>
                  <Typography variant="body2" color="text.secondary" fontWeight="600" textTransform="uppercase">
                    {stat.title}
                  </Typography>
                  <Typography variant="h5" fontWeight="700" sx={{ mt: 0.5, color: '#1e293b' }}>
                    {stat.value}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3, boxShadow: 'none', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                Biểu đồ Nhiệt độ & Độ ẩm (Gần đây)
              </Typography>
              <Box sx={{ width: '100%', height: 350 }}>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorHum" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                      <Tooltip 
                        contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                      <Area type="monotone" dataKey="temp" name="Nhiệt độ (°C)" stroke="#ef4444" fillOpacity={1} fill="url(#colorTemp)" />
                      <Area type="monotone" dataKey="hum" name="Độ ẩm (%)" stroke="#3b82f6" fillOpacity={1} fill="url(#colorHum)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <Typography color="text.secondary">Đang tải dữ liệu biểu đồ...</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, boxShadow: 'none', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                Nhật ký & Cảnh báo
              </Typography>
              <List sx={{ p: 0 }}>
                {alerts.map((alert, idx) => (
                  <React.Fragment key={alert.id}>
                    <ListItem alignItems="flex-start" sx={{ px: 1, py: 1.5 }}>
                      <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                        <Notifications color={alert.acknowledged ? 'disabled' : (alert.severity === 'Error' ? 'error' : 'warning')} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" fontWeight="600" color={alert.acknowledged ? 'text.secondary' : 'text.primary'}>
                            {alert.title}
                          </Typography>
                        }
                        secondary={
                          <React.Fragment>
                            <Typography component="span" variant="caption" color="text.secondary" display="block">
                              {new Date(alert.created_at).toLocaleTimeString()} - {alert.room_id}
                            </Typography>
                            <Typography component="span" variant="body2" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              {alert.message}
                            </Typography>
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    {idx < alerts.length - 1 && <Divider component="li" />}
                  </React.Fragment>
                ))}
                {alerts.length === 0 && (
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
                    Hệ thống hoạt động ổn định, không có cảnh báo.
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

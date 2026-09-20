import React, { useContext } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { 
  Box, Drawer, List, ListItem, ListItemIcon, ListItemText, 
  AppBar, Toolbar, Typography, Button, Avatar, IconButton, Divider, ListItemButton 
} from '@mui/material';
import { 
  Dashboard, Videocam, Devices, Settings, 
  Notifications, History, School, Logout 
} from '@mui/icons-material';

const drawerWidth = 260;

export default function Layout() {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const menu = [
    { text: 'Tổng quan', icon: <Dashboard />, path: '/' },
    { text: 'Phòng học', icon: <School />, path: '/rooms' },
    { text: 'Thiết bị IoT', icon: <Devices />, path: '/devices' },
    { text: 'Dữ liệu cảm biến', icon: <History />, path: '/telemetry' },
    { text: 'Camera AI', icon: <Videocam />, path: '/camera' },
    { text: 'Điều khiển', icon: <Settings />, path: '/control' },
    { text: 'Cảnh báo', icon: <Notifications />, path: '/alerts' }
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#ffffff',
          color: '#1e293b',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)'
        }}
      >
        <Toolbar>
          <School sx={{ mr: 2, color: 'primary.main' }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 700, color: 'primary.main' }}>
            SMART CLASSROOM AIoT
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" fontWeight="500">Admin User</Typography>
            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>A</Avatar>
            <IconButton color="error" onClick={auth.logout} title="Đăng xuất">
              <Logout />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { 
            width: drawerWidth, 
            boxSizing: 'border-box',
            borderRight: 'none',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <List sx={{ px: 2 }}>
            {menu.map((item, index) => {
              const active = location.pathname === item.path;
              return (
                <ListItem key={index} disablePadding sx={{ mb: 1 }}>
                  <ListItemButton 
                    onClick={() => navigate(item.path)}
                    sx={{
                      borderRadius: 2,
                      backgroundColor: active ? 'rgba(255,255,255,0.1)' : 'transparent',
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.2)',
                      }
                    }}
                  >
                    <ListItemIcon sx={{ color: active ? '#60a5fa' : '#94a3b8', minWidth: 40 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.text} 
                      primaryTypographyProps={{ 
                        fontWeight: active ? 600 : 400,
                        color: active ? '#ffffff' : '#cbd5e1'
                      }} 
                    />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 4, pt: 10, minHeight: '100vh' }}>
        <Outlet />
      </Box>
    </Box>
  );
}

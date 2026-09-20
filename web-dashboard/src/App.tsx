import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './contexts/AuthContext';
import Login from './pages/Login';
import Layout from './components/Layout';
import DashboardPage from './pages/Dashboard';
import CameraPage from './pages/Camera';
import DevicesPage from './pages/Devices';
import TelemetryPage from './pages/Telemetry';
import ControlPage from './pages/Control';
import AlertsPage from './pages/Alerts';
import RoomsPage from './pages/Rooms';

const ProtectedRoute = ({ children }: { children: any }) => {
  const auth = useContext(AuthContext);
  if (!auth?.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="rooms" element={<RoomsPage />} />
          <Route path="devices" element={<DevicesPage />} />
          <Route path="telemetry" element={<TelemetryPage />} />
          <Route path="camera" element={<CameraPage />} />
          <Route path="control" element={<ControlPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="*" element={<div>Page not found or under construction</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

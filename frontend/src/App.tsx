import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import AdminGate from "./components/AdminGate";
import Shell from "./components/Shell";
import About from "./pages/About";
import AdminHome from "./pages/AdminHome";
import Catalog from "./pages/Catalog";
import Compare from "./pages/Compare";
import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import DeviceDetails from "./pages/DeviceDetails";
import Landing from "./pages/Landing";
import Models from "./pages/Models";
import Predict from "./pages/Predict";
import { PredictionHistory, PredictionView } from "./pages/PredictionHistory";

function ScrollTop() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return null;
}

export default function App() {
  return (
    <>
      <ScrollTop />
      <Routes>
        <Route element={<Shell wide />}>
          <Route path="/" element={<Landing />} />
          <Route path="/about" element={<About />} />
        </Route>
        <Route element={<Shell />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/smartphones" element={<Catalog category="Smartphone" />} />
          <Route path="/laptops" element={<Catalog category="Laptop" />} />
          <Route path="/devices" element={<Catalog />} />
          <Route path="/devices/:id" element={<DeviceDetails />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/predictions" element={<PredictionHistory />} />
          <Route path="/predictions/:id" element={<PredictionView />} />
          {/* Administration needs the administrator key (checked by the server); everything above is public. */}
          <Route element={<AdminGate><Outlet /></AdminGate>}>
            <Route path="/admin" element={<AdminHome />} />
            <Route path="/admin/datasets" element={<Datasets />} />
            <Route path="/admin/models" element={<Models />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

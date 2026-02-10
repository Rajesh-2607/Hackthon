import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import Index from "./pages/Index";
import Detection from "./pages/Detection";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Placeholder from "./pages/Placeholder";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/detection" element={<Detection />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/reports" element={<Placeholder title="Reports" description="Advanced analytics and detailed reports coming soon." />} />
          <Route path="/settings" element={<Placeholder title="Settings" description="Configure your Secure Sphere account settings." />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<Placeholder title="Page Not Found" description="The page you're looking for doesn't exist." />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

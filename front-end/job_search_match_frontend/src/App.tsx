import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { JobSearchProvider } from "@/contexts/JobSearchContext";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { ProfilePage } from "@/pages/ProfilePage";
import { JobSearchPage } from "@/pages/JobSearchPage";
import { JobResultsPage } from "@/pages/JobResultsPage";
import { JobDetailPage } from "@/pages/JobDetailPage";
import { JobMatchedPage } from "@/pages/JobMatchedPage";
function App() {
  return (
    <AuthProvider>
      <JobSearchProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-gray-50">
            <Navbar />
          <main className="flex-grow">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected routes */}
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/search" element={<JobSearchPage />} />
              <Route path="/search_results" element={<JobResultsPage />} />
              <Route path="/matches" element={<JobMatchedPage />} />
              <Route path="/jobs/:jobId" element={<JobDetailPage />} />

              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/profile" replace />} />
              <Route path="*" element={<Navigate to="/profile" replace />} />
            </Routes>
          </main> 
          <Footer />
        </div>
      </Router>
    </JobSearchProvider>
    </AuthProvider>
  );
}

export default App;

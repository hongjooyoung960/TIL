import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DailyPage } from "./pages/DailyPage";
import { GoalsPage } from "./pages/GoalsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { WeeklyPage } from "./pages/WeeklyPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DailyPage />} />
          <Route path="weekly" element={<WeeklyPage />} />
          <Route path="goals" element={<GoalsPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

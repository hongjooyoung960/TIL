import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "일간 플래너" },
  { to: "/weekly", label: "주간 플래너" },
  { to: "/goals", label: "목표" },
  { to: "/reports", label: "리포트·Git" },
];

export function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h2 style={{ marginTop: 0 }}>Planner</h2>
        <nav>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === "/"} className={({ isActive }) => (isActive ? "active" : "")}>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}

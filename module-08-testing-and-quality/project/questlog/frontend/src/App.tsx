import { Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { SignupPage } from "./pages/SignupPage";
import { QuestListPage } from "./pages/QuestListPage";
import { NewQuestPage } from "./pages/NewQuestPage";
import { QuestDetailPage } from "./pages/QuestDetailPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/**
 * The route table. `<Layout>` renders the header/nav once and an
 * `<Outlet />` where its matched child route goes -- see
 * lessons/08-react-router.md (Module 04) for the full explanation of
 * nested routes, `index`, dynamic segments (`:id`), and the catch-all `*`
 * route.
 *
 * New in Module 07: `/login` and `/signup` are deliberately **outside**
 * `<Layout>`'s nested tree and require no `<ProtectedRoute>` wrapper at
 * all -- you must be able to reach them precisely when you're *not*
 * logged in. Every route nested inside `<Layout>` except the catch-all
 * `*` is now wrapped in `<ProtectedRoute>` (src/components/
 * ProtectedRoute.tsx), which redirects to `/login` if `useAuth()` has no
 * user. See lessons/07-protecting-routes-with-dependencies.md for why
 * this frontend-side check is a UX convenience layered on top of the
 * backend's own, mandatory enforcement -- not a replacement for it.
 */
function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/" element={<Layout />}>
        <Route
          index
          element={
            <ProtectedRoute>
              <QuestListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="quests/new"
          element={
            <ProtectedRoute>
              <NewQuestPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="quests/:id"
          element={
            <ProtectedRoute>
              <QuestDetailPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;

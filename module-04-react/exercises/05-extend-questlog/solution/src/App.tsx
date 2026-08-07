import { Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { QuestListPage } from "./pages/QuestListPage";
import { NewQuestPage } from "./pages/NewQuestPage";
import { QuestDetailPage } from "./pages/QuestDetailPage";
import { QuestLinesPage } from "./pages/QuestLinesPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/**
 * The route table. `<Layout>` renders the header/nav once and an
 * `<Outlet />` where its matched child route goes -- see
 * lessons/08-react-router.md for the full explanation of nested routes,
 * `index`, dynamic segments (`:id`), and the catch-all `*` route.
 */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<QuestListPage />} />
        <Route path="quests/new" element={<NewQuestPage />} />
        <Route path="quests/:id" element={<QuestDetailPage />} />
        {/* Exercise 05: a new route, added with no changes needed to any
            existing route -- this is exactly the kind of change a nested
            route tree is designed to make easy. */}
        <Route path="quest-lines" element={<QuestLinesPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;

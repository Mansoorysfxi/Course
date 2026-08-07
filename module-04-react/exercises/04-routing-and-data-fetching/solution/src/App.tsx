import { Route, Routes } from "react-router";
import { CatalogPage } from "./pages/CatalogPage";
import { ItemDetailPage } from "./pages/ItemDetailPage";
import { NotFoundPage } from "./pages/NotFoundPage";

function App() {
  return (
    <div>
      <h1>Merchant Catalog</h1>
      <Routes>
        <Route index element={<CatalogPage />} />
        <Route path="items/:id" element={<ItemDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
}

export default App;

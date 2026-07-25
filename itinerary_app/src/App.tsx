import React, { useState, useEffect } from "react";
import { Plus, Trash2, MapPin, DollarSign, Clock } from "lucide-react";
import { getItems, addItem, deleteItem, ItineraryItem } from "./firebase";
import "./App.css";

function App() {
  const [attractions, setAttractions] = useState<ItineraryItem[]>([]);
  const [restaurants, setRestaurants] = useState<ItineraryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [showAddForm, setShowAddForm] = useState<"attraction" | "restaurant" | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    category: "",
    location: "",
    price: "",
    memo: "",
    googleMapsLink: "",
  });

  useEffect(() => {
    loadItems();
  }, []);

  async function loadItems() {
    setLoading(true);
    try {
      const items = await getItems();
      setAttractions(items.filter((i) => i.type === "attraction"));
      setRestaurants(items.filter((i) => i.type === "restaurant"));
    } catch (error) {
      console.error("Failed to load items:", error);
    }
    setLoading(false);
  }

  async function handleAdd() {
    if (!formData.name) return alert("이름을 입력하세요");

    try {
      await addItem({
        type: showAddForm === "attraction" ? "attraction" : "restaurant",
        name: formData.name,
        category: formData.category,
        location: formData.location,
        price: formData.price,
        memo: formData.memo,
        googleMapsLink: formData.googleMapsLink,
      });

      setFormData({
        name: "",
        category: "",
        location: "",
        price: "",
        memo: "",
        googleMapsLink: "",
      });
      setShowAddForm(null);
      await loadItems();
    } catch (error) {
      console.error("Failed to add item:", error);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("삭제하시겠습니까?")) return;
    try {
      await deleteItem(id);
      await loadItems();
    } catch (error) {
      console.error("Failed to delete item:", error);
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen">로딩 중...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-900">상하이 여행 일정 ✈️</h1>
        <p className="text-center text-gray-600 mb-8">2026.7.27-7.30 (3박 4일)</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 관광지 */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <MapPin size={28} />
                관광지
              </h2>
              <button
                onClick={() => setShowAddForm("attraction")}
                className="mt-4 w-full bg-white text-blue-600 py-2 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 hover:bg-gray-50 transition"
              >
                <Plus size={20} /> 관광지 추가
              </button>
            </div>

            <div className="p-6 space-y-3 max-h-[600px] overflow-y-auto">
              {attractions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">관광지를 추가하세요</p>
              ) : (
                attractions.map((item) => (
                  <AttractionCard
                    key={item.id}
                    item={item}
                    onDelete={() => handleDelete(item.id)}
                  />
                ))
              )}
            </div>
          </div>

          {/* 맛집 */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-orange-500 to-red-600 p-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <DollarSign size={28} />
                맛집
              </h2>
              <button
                onClick={() => setShowAddForm("restaurant")}
                className="mt-4 w-full bg-white text-red-600 py-2 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 hover:bg-gray-50 transition"
              >
                <Plus size={20} /> 맛집 추가
              </button>
            </div>

            <div className="p-6 space-y-3 max-h-[600px] overflow-y-auto">
              {restaurants.length === 0 ? (
                <p className="text-gray-500 text-center py-8">맛집을 추가하세요</p>
              ) : (
                restaurants.map((item) => (
                  <RestaurantCard
                    key={item.id}
                    item={item}
                    onDelete={() => handleDelete(item.id)}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* 추가 폼 모달 */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
              <h3 className="text-2xl font-bold mb-4">
                {showAddForm === "attraction" ? "관광지" : "맛집"} 추가
              </h3>

              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="이름"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                {showAddForm === "attraction" ? (
                  <>
                    <input
                      type="text"
                      placeholder="카테고리 (예: 도보, 디디 10분)"
                      value={formData.category}
                      onChange={(e) =>
                        setFormData({ ...formData, category: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="입장료"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </>
                ) : (
                  <>
                    <input
                      type="text"
                      placeholder="음식 종류 (예: 양꼬치, 샤오롱바오)"
                      value={formData.category}
                      onChange={(e) =>
                        setFormData({ ...formData, category: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="위치"
                      value={formData.location}
                      onChange={(e) =>
                        setFormData({ ...formData, location: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder="가격 (예: ¥100~)"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </>
                )}

                <textarea
                  placeholder="메모"
                  value={formData.memo}
                  onChange={(e) => setFormData({ ...formData, memo: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 h-20 resize-none"
                />

                <input
                  type="url"
                  placeholder="구글맵 링크"
                  value={formData.googleMapsLink}
                  onChange={(e) =>
                    setFormData({ ...formData, googleMapsLink: e.target.value })
                  }
                  className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowAddForm(null)}
                  className="flex-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-lg font-semibold hover:bg-gray-400 transition"
                >
                  취소
                </button>
                <button
                  onClick={handleAdd}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  추가
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function AttractionCard({
  item,
  onDelete,
}: {
  item: ItineraryItem;
  onDelete: () => void;
}) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-4 rounded-lg hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-bold text-lg text-gray-900">{item.name}</h4>
        <button
          onClick={onDelete}
          className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {item.category && (
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">카테고리:</span> {item.category}
        </p>
      )}
      {item.price && (
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">입장료:</span> {item.price}
        </p>
      )}
      {item.memo && (
        <p className="text-sm text-gray-700 italic mb-2">💡 {item.memo}</p>
      )}
      {item.googleMapsLink && (
        <a
          href={item.googleMapsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1"
        >
          📍 지도보기
        </a>
      )}
    </div>
  );
}

function RestaurantCard({
  item,
  onDelete,
}: {
  item: ItineraryItem;
  onDelete: () => void;
}) {
  return (
    <div className="bg-gradient-to-br from-orange-50 to-red-50 border-l-4 border-orange-500 p-4 rounded-lg hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h4 className="font-bold text-lg text-gray-900">{item.name}</h4>
          {item.category && (
            <p className="text-xs text-gray-600">🍽️ {item.category}</p>
          )}
        </div>
        <button
          onClick={onDelete}
          className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {item.location && (
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">위치:</span> {item.location}
        </p>
      )}
      {item.price && (
        <p className="text-sm text-gray-600 mb-1">
          <span className="font-semibold">가격:</span> {item.price}
        </p>
      )}
      {item.memo && (
        <p className="text-sm text-gray-700 italic mb-2">💡 {item.memo}</p>
      )}
      {item.googleMapsLink && (
        <a
          href={item.googleMapsLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1"
        >
          📍 지도보기
        </a>
      )}
    </div>
  );
}

export default App;

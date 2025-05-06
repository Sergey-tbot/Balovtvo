ProductionPriceInfo = {}
ProductionPriceInfo_mt = Class(ProductionPriceInfo)

function ProductionPriceInfo:new()
    local self = setmetatable({}, ProductionPriceInfo_mt)
    self.ui = nil
    self.txtCurrentPrice = nil
    self.txtMaxPrice = nil
    return self
end

function ProductionPriceInfo:load()
    -- Загружаем наш UI из xml
    self.ui = g_gui:loadGui(g_currentModDirectory .. "ui/ProductionPriceInfo.xml")
    
    -- Получаем ссылки на текстовые элементы
    self.txtCurrentPrice = self.ui:getElementById("txtCurrentPrice")
    self.txtMaxPrice = self.ui:getElementById("txtMaxPrice")

    -- Подписываемся на событие открытия окна цепочек производства
    -- В FS25 нет прямого события, поэтому будем обновлять цены при каждом обновлении интерфейса
    -- Для этого добавим наш update в глобальный update
    addModEventListener(self)
end

function ProductionPriceInfo:update(dt)
    -- Проверяем, открыто ли окно цепочек производства
    if g_gui:getIsGuiVisible() and g_gui.currentGuiName == "productionChain" then
        self:updatePrices()
        -- Показываем наш UI поверх
        if not self.ui:getIsVisible() then
            self.ui:setVisible(true)
        end
    else
        -- Скрываем UI, если окно не открыто
        if self.ui:getIsVisible() then
            self.ui:setVisible(false)
        end
    end
end

function ProductionPriceInfo:updatePrices()
    local productionChain = g_currentMission.productionChainManager.productionChain -- пример, нужно проверить реальное имя
    
    if productionChain == nil then
        -- Если цепочка не загружена, очистим текст
        self.txtCurrentPrice:setText("Текущая цена продажи: -")
        self.txtMaxPrice:setText("Максимальная цена продажи: -")
        return
    end

    local maxCurrentPrice = 0
    local maxPriceFromDiagram = 0

    -- Перебираем все продукты в цепочке производства
    for _, product in pairs(productionChain.products) do
        local productId = product.id
        
        -- Получаем максимальную текущую цену продажи среди всех точек продажи
        local currentPrice = self:getMaxCurrentPrice(productId)
        if currentPrice > maxCurrentPrice then
            maxCurrentPrice = currentPrice
        end

        -- Получаем максимальную цену из диаграммы цен
        local maxPrice = self:getMaxPriceFromDiagram(productId)
        if maxPrice > maxPriceFromDiagram then
            maxPriceFromDiagram = maxPrice
        end
    end

    -- Обновляем текст в UI
    self.txtCurrentPrice:setText(string.format("Текущая цена продажи: %.2f", maxCurrentPrice))
    self.txtMaxPrice:setText(string.format("Максимальная цена продажи: %.2f", maxPriceFromDiagram))
end

function ProductionPriceInfo:getMaxCurrentPrice(productId)
    local maxPrice = 0
    if g_currentMission.sellPoints == nil then
        return 0
    end

    for _, sellPoint in pairs(g_currentMission.sellPoints) do
        local price = sellPoint:getPrice(productId)
        if price > maxPrice then
            maxPrice = price
        end
    end
    return maxPrice
end

function ProductionPriceInfo:getMaxPriceFromDiagram(productId)
    if g_currentMission.priceManager == nil then
        return 0
    end
    local maxPrice = g_currentMission.priceManager:getMaxPrice(productId)
    if maxPrice == nil then
        return 0
    end
    return maxPrice
end

-- Инициализация мода при загрузке игры
function ProductionPriceInfo:loadMap(name)
    self:load()
end

addModEventListener(ProductionPriceInfo:new())

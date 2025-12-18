import os

file_path = r'd:\Python\Mathproject\templates\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# --- HTML Replacement ---
# Marker 1: Start of the container fluid block
start_marker_html = '<!-- 重構：置中對齊的對話框容器 (消除右側空白) -->'
# Marker 2: End of the block (before The Image Modal)
end_marker_html = '<!-- The Image Modal -->'

html_replacement = """        <!-- 重構：置中對齊的對話框容器 (消除右側空白) -->
        <div class="container-fluid py-4">
            <div class="row justify-content-center">
                <div class="col-12 col-lg-10 mx-auto">
                    <div class="card shadow-sm border-0 chat-card" style="height: 80vh; display: flex; flex-direction: column;">
                        
                        <div id="chat-messages" class="card-body p-4" style="flex: 1; overflow-y: auto; background-color: #fcfcfc;">
                            <!-- 預設訊息 -->
                            <div class="bot-message">
                                <div style="margin: 0; padding: 0; font-weight: bold; line-height: 1.2;">你好！有問題問我～</div>
                            </div>
                        </div>

                        <div class="card-footer bg-white border-top p-3">
                            
                            <div id="static-prompt-container" class="mb-2">
                                <div class="text-muted mb-1" style="font-size: 0.75rem;"><i class="fas fa-anchor"></i> 單元核心引導</div>
                                <div id="static-prompts" class="d-flex flex-wrap gap-2"></div>
                            </div>

                            <div id="dynamic-prompt-container" class="mb-3" style="display: none;">
                                <div class="text-muted mb-1" style="font-size: 0.75rem;"><i class="fas fa-magic"></i> 針對剛才的回覆，你可以問...</div>
                                <div id="dynamic-prompts" class="d-flex flex-wrap gap-2"></div>
                            </div>

                            <!-- Symbol Buttons (Integrate back) -->
                             <div class="symbol-buttons mb-2" style="display: flex; gap: 3px; flex-wrap: wrap;">
                                <button class="symbol-button" data-symbol="π">π</button><button class="symbol-button" data-symbol="√">√</button>
                                <button class="symbol-button" data-symbol="²">²</button><button class="symbol-button" data-symbol="³">³</button>
                                <button class="symbol-button" data-symbol="°">°</button><button class="symbol-button" data-symbol="θ">θ</button>
                                <button class="symbol-button" data-symbol="∞">∞</button><button class="symbol-button" data-symbol="±">±</button>
                                <button class="symbol-button" data-symbol="≠">≠</button><button class="symbol-button" data-symbol="≤">≤</button>
                                <button class="symbol-button" data-symbol="≥">≥</button><button class="symbol-button" data-symbol="≈">≈</button>
                                <button class="symbol-button" data-symbol="∑">∑</button><button class="symbol-button" data-symbol="∫">∫</button>
                             </div>

                            <div class="input-group">
                                <input type="text" id="chat-input" class="form-control form-control-lg" placeholder="輸入您的問題...">
                                <button id="chat-send-button" class="btn btn-primary px-4">
                                    <i class="fas fa-paper-plane"></i> 發送
                                </button>
                                <input type="file" id="image-uploader" accept="image/*" style="display: none;">
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    """

# Calculate replacement
try:
    s_idx = content.index(start_marker_html)
    e_idx = content.index(end_marker_html)
    # The replacement above includes closing divs, so we replace everything up to end_marker
    # Check if end_marker is included or excluded. We want to KEEP end_marker.
    # We replace content[s_idx : e_idx]
    
    # However, we must match the *exact* indentation of the previous block to look nice, 
    # but since we are replacing the whole block, direct injection is fine.
    
    new_content = content[:s_idx] + html_replacement + content[e_idx:]
    print("HTML replacement prepared.")
except ValueError as e:
    print(f"HTML Markers not found: {e}")
    new_content = content # Fallback

# --- JS Replacement ---
# Marker: renderStaticPrompts function definition
js_start_marker = '// 顯示初始固定建議 (Primary Blue Style)'
# Marker: End of updateSuggestedPrompts
js_end_marker = '// 頁面載入：渲染固定建議'

js_replacement = """        // Modify renderStaticPrompts 確保它填入 static-prompts
        function renderStaticPrompts(prompts) {
            const container = document.getElementById('static-prompts');
            if (!container) return;
            container.innerHTML = '';
            prompts.forEach(p => {
                if (!p || p === 'None' || !p.trim()) return;
                const btn = document.createElement('button');
                btn.className = 'btn btn-outline-primary btn-sm px-3 mb-2'; // Keep mb-2 for spacing
                btn.innerHTML = p;
                btn.onclick = () => { 
                    const input = document.getElementById('chat-input');
                    if(input) input.value = p; 
                };
                container.appendChild(btn);
            });
            if (window.MathJax) try { window.MathJax.typesetPromise([container]); } catch (e) { }
        }

        // Modify updateSuggestedPrompts 確保它填入 dynamic-prompts
        function updateSuggestedPrompts(prompts) {
            const container = document.getElementById('dynamic-prompts');
            const wrapper = document.getElementById('dynamic-prompt-container');
            if (!container) return;
            
            container.innerHTML = '';
            if (prompts && prompts.length > 0) {
                if(wrapper) wrapper.style.display = 'block'; // 顯示容器
                
                prompts.forEach(p => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-info btn-sm rounded-pill px-3 mb-2';
                    btn.innerHTML = p;
                    btn.onclick = () => { 
                        const input = document.getElementById('chat-input');
                        if(input) {
                            input.value = p;
                        }
                    };
                    container.appendChild(btn);
                });
                
                if (window.MathJax) {
                    window.MathJax.typesetPromise([container]).catch(err => console.log(err));
                }
            } else {
                if(wrapper) wrapper.style.display = 'none';
            }
        }

        """

try:
    js_s_idx = new_content.index(js_start_marker)
    js_e_idx = new_content.index(js_end_marker)
    
    final_content = new_content[:js_s_idx] + js_replacement + new_content[js_e_idx:]
    print("JS replacement prepared.")
except ValueError as e:
    print(f"JS Markers not found: {e}")
    final_content = new_content

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Done.")

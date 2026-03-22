import os
import re

def convert_theme(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    
    # 1. Strip glassmorphism
    content = re.sub(r'backdrop-filter:\s*blur\([^)]+\);', '', content)
    
    # 2. Strip glowing text and box shadows
    content = re.sub(r'text-shadow:\s*0\s*0\s*\d+px\s*[^;]+;', '', content)
    content = re.sub(r'box-shadow:\s*0\s*0\s*\d+px\s*[^;]+;', 'box-shadow: none;', content)
    
    # 3. Replace base CSS variables in Home.vue / elsewhere
    content = content.replace('--bg-dark: #050d1a;', '--bg-dark: #111111;')
    content = content.replace('--bg-card: #0a1628;', '--bg-card: #1C1C1F;')
    content = content.replace('--bg-panel: #0d1e35;', '--bg-panel: #252529;')
    content = content.replace('--accent-blue: #0ea5e9;', '--accent-blue: #7856FF;') # Mixpanel purple replacing blue
    content = content.replace('--border: rgba(14, 165, 233, 0.15);', '--border: #38383F;')
    
    # 4. Flatten specific hardcoded transparent backgrounds
    content = content.replace('background: rgba(5, 13, 26, 0.95);', 'background: var(--bg-card);')
    content = content.replace('background: rgba(14, 165, 233, 0.08);', 'background: var(--bg-panel);')
    content = content.replace('background: rgba(14, 165, 233, 0.06);', 'background: var(--bg-panel);')
    content = content.replace('background: rgba(14, 165, 233, 0.02);', 'background: var(--bg-panel);')
    content = content.replace('background: rgba(14, 165, 233, 0.12);', 'background: #2A2A35;')
    content = content.replace('background: rgba(14, 165, 233, 0.2);', 'background: #7856FF;')
    
    # 5. Fix border colors to flat
    content = content.replace('border: 1px solid rgba(14, 165, 233, 0.25);', 'border: 1px solid var(--border);')
    content = content.replace('border: 1px solid rgba(14, 165, 233, 0.15);', 'border: 1px solid var(--border);')
    content = content.replace('border: 1px solid rgba(14, 165, 233, 0.2);', 'border: 1px solid var(--border);')
    content = content.replace('border: 1px solid rgba(14, 165, 233, 0.12);', 'border: 1px solid var(--border);')
    
    # Text colors
    content = content.replace('color: rgba(14, 165, 233, 0.25);', 'color: #7856FF;')
    content = content.replace('color: rgba(14, 165, 233, 0.3);', 'color: #7856FF;')
    content = content.replace('color: rgba(14, 165, 233, 0.4);', 'color: #7856FF;')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated theme in: {filepath}")

def main():
    base_dir = r"C:\Users\Nirav\.vscode\projects\MiroFish\frontend\src"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.vue', '.css')):
                convert_theme(os.path.join(root, file))

if __name__ == "__main__":
    main()

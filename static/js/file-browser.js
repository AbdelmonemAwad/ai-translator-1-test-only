// File Browser JavaScript Functions
let currentInputField = null;
let currentBrowserPath = '/';

function openFileBrowser(inputId) {
    console.log('Opening file browser for:', inputId);
    currentInputField = inputId;
    const modal = document.getElementById('file-browser-modal');
    const currentInput = document.getElementById(inputId);
    
    if (!modal) {
        console.error('File browser modal not found');
        alert('خطأ: نافذة تصفح الملفات غير موجودة');
        return;
    }
    
    if (!currentInput) {
        console.error('Input field not found:', inputId);
        alert('خطأ: حقل الإدخال غير موجود');
        return;
    }
    
    // Set initial path from current input value or default to /
    currentBrowserPath = currentInput.value || '/';
    
    const currentPathEl = document.getElementById('current-path');
    const selectedPathEl = document.getElementById('selected-path');
    
    if (currentPathEl) currentPathEl.textContent = currentBrowserPath;
    if (selectedPathEl) selectedPathEl.textContent = currentBrowserPath;
    
    console.log('Showing modal for path:', currentBrowserPath);
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    
    console.log('Modal display style:', modal.style.display);
    console.log('Modal computed style:', window.getComputedStyle(modal).display);
    
    loadFolders(currentBrowserPath);
}

function closeFileBrowser() {
    const modal = document.getElementById('file-browser-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentInputField = null;
}

function selectPath() {
    if (currentInputField) {
        document.getElementById(currentInputField).value = currentBrowserPath;
    }
    closeFileBrowser();
}

function loadFolders(path) {
    const loadingDiv = document.getElementById('folder-loading');
    const folderList = document.getElementById('folder-list');
    
    loadingDiv.style.display = 'flex';
    folderList.innerHTML = '';
    
    // Real API call to browse folders
    fetch('/api/browse-folders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: path })
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = 'none';
        
        if (data.success) {
            folderList.innerHTML = '';
            
            // Add parent directory option
            if (path !== '/') {
                const parentPath = path.split('/').slice(0, -1).join('/') || '/';
                const parentItem = createFolderItem('..', parentPath, true);
                folderList.appendChild(parentItem);
            }
            
            // Add folders
            data.folders.forEach(folder => {
                const folderItem = createFolderItem(folder.name, folder.path, false);
                folderList.appendChild(folderItem);
            });
        } else {
            folderList.innerHTML = '<li style="padding: 15px; color: var(--text-error);">خطأ في تحميل المجلدات: ' + data.error + '</li>';
        }
    })
    .catch(error => {
        loadingDiv.style.display = 'none';
        folderList.innerHTML = '<li style="padding: 15px; color: var(--text-error);">خطأ في الاتصال بالخادم</li>';
        console.error('Error loading folders:', error);
    });
}

function createFolderItem(name, path, isParent) {
    const li = document.createElement('li');
    if (!li) return null;
    
    li.className = 'folder-item';
    li.onclick = () => {
        if (li && path) {
            selectFolder(path, li);
        }
    };
    
    li.innerHTML = `
        <div class="folder-icon">
            ${isParent ? '⬆️' : '📁'}
        </div>
        <div class="folder-name">${name}</div>
    `;
    
    // Double click to navigate
    li.ondblclick = () => {
        if (isParent || name !== '..') {
            navigateToFolder(path);
        }
    };
    
    return li;
}

function selectFolder(path, element) {
    // Remove previous selection
    document.querySelectorAll('.folder-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Add selection to current item
    element.classList.add('selected');
    currentBrowserPath = path;
    
    // Update displays
    const currentPathEl = document.getElementById('current-path');
    const selectedPathEl = document.getElementById('selected-path');
    
    if (selectedPathEl) selectedPathEl.textContent = path;
}

function navigateToFolder(path) {
    currentBrowserPath = path;
    const currentPathEl = document.getElementById('current-path');
    const selectedPathEl = document.getElementById('selected-path');
    
    if (currentPathEl) currentPathEl.textContent = path;
    if (selectedPathEl) selectedPathEl.textContent = path;
    
    loadFolders(path);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Make functions globally accessible
    window.openFileBrowser = openFileBrowser;
    window.closeFileBrowser = closeFileBrowser;
    window.selectPath = selectPath;
    
    // Close modal when clicking outside
    const modal = document.getElementById('file-browser-modal');
    if (modal) {
        modal.onclick = function(e) {
            if (e.target === this) {
                closeFileBrowser();
            }
        };
    }
});
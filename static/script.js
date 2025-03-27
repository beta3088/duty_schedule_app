document.addEventListener('DOMContentLoaded', function() {
    const draggables = document.querySelectorAll('.draggable');
    let draggedItem = null;

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', (e) => {
            if (sessionRole === 'admin') {
                draggedItem = e.target;
                draggedItem.classList.add('dragging');
            } else {
                e.preventDefault(); // Prevent dragging for non-admin users
            }
        });

        draggable.addEventListener('dragend', () => {
            if (draggedItem) {
                draggedItem.classList.remove('dragging');
                draggedItem = null;
            }
        });

        draggable.addEventListener('dragover', (e) => {
            if (draggedItem && e.target.classList.contains('draggable') && draggedItem !== e.target) {
                e.preventDefault();
            }
        });

        draggable.addEventListener('drop', (e) => {
            if (draggedItem && e.target.classList.contains('draggable') && draggedItem !== e.target) {
                const date1 = draggedItem.dataset.date;
                const date2 = e.target.dataset.date;

                fetch('/swap_schedule', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ date1: date1, date2: date2 })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('调换失败，请查看日志。');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('发生错误，请重试。');
                });
            }
        });
    });

    // 获取用户角色 (从 HTML 中获取，在模板中设置)
    const sessionRoleElement = document.getElementById('session-role');
    const sessionRole = sessionRoleElement ? sessionRoleElement.textContent : null;
});
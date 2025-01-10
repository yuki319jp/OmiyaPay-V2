// グローバルな関数や初期化処理
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrapのツールチップを有効化
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // フラッシュメッセージの自動非表示
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 3000);
});

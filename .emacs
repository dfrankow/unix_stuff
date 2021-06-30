;; Python checking
;; (custom-set-variables
;;   '(py-pychecker-command "pychecker.sh")
;;   '(py-pychecker-command-args (quote ("")))
;;   '(python-check-command "pychecker.sh")
;; )

;; Show column numbers
(setq column-number-mode t)

;; No tabs!
(setq-default indent-tabs-mode nil)

;; Draw tabs with the same color as trailing whitespace
    ;; (add-hook 'font-lock-mode-hook
    ;;           (lambda ()
    ;;             (font-lock-add-keywords
    ;;               nil
    ;;               '(("\t" 0 'trailing-whitespace prepend)))))

;; match parens (forward and backward) stolen from 'emacs.faq'
(global-set-key "?" 'match-paren)
(defun match-paren (arg)
  "Go to the matching parenthesis if on parenthesis otherwise insert ?."
  (interactive "p")
  (cond ((looking-at "\\s\(") (forward-list 1) (backward-char 1))
        ((looking-at "\\s\)") (forward-char 1) (backward-list 1))
        (t (self-insert-command (or arg 1)))))

;; Package management
(when (>= emacs-major-version 24)
  (require 'package)
  (package-initialize)
  (add-to-list 'package-archives '("melpa" . "http://melpa.milkbox.net/packages/") t)
  (add-to-list 'package-archives '("marmalade" . "http://marmalade-repo.org/") t)
  )

;; Scala
; (unless (package-installed-p 'scala-mode2)
;  (package-refresh-contents) (package-install 'scala-mode2))

(require 'sql)
(add-to-list 'auto-mode-alist '("\\.q$" . sql-mode))
(add-to-list 'auto-mode-alist '("\\.ql$" . sql-mode))

;; delete trailing whitespace upon save
;; A little dangerous, but 99/100 times I want it
;; (add-hook 'before-save-hook 'delete-trailing-whitespace)

;; See https://www.emacswiki.org/emacs/FileNameCache
(require 'filecache)
;;Used to have a 'schemas' directory:
;;(file-cache-add-directory-using-find "/Users/dan/work/schemas")
;; Add files to file cache when killing the buffer
(defun file-cache-add-this-file ()
  (and buffer-file-name
       (file-exists-p buffer-file-name)
       (file-cache-add-file buffer-file-name)))
(add-hook 'kill-buffer-hook 'file-cache-add-this-file)

;; javascript indent 2 spaces
(setq js-indent-level 2)

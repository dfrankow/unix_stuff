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
(unless (package-installed-p 'scala-mode2)
  (package-refresh-contents) (package-install 'scala-mode2))

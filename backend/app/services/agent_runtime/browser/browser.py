from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


class BrowserAutomation:

    def __init__(
        self,
        headless: bool = False,
        user_data_dir: str = ".browser_profile",
    ):
        self.headless = headless
        self.user_data_dir = Path(user_data_dir).resolve()

    def _start(self):
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
        )

        page = context.pages[0] if context.pages else context.new_page()

        return playwright, context, page


    def find_create_button(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            if "accounts.google.com" in page.url:
                return {
                    "success": False,
                    "logged_in": False,
                    "status": "login_required",
                }

            create_button = page.get_by_text(
                "Create",
                exact=True,
            )

            count = create_button.count()

            return {
                "success": True,
                "logged_in": True,
                "status": (
                    "create_button_found"
                    if count
                    else "create_button_not_found"
                ),
                "count": count,
                "url": page.url,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "browser_error",
                "error": str(exc),
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def click_create_button(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)
            count = create_button.count()

            if count == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                    "url": page.url,
                }

            create_button.first.click()
            page.wait_for_timeout(1_500)

            return {
                "success": True,
                "status": "create_button_clicked",
                "url": page.url,
                "count": count,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "click_failed",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def inspect_create_menu(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                    "url": page.url,
                }

            create_button.first.click()

            page.wait_for_timeout(1_000)

            visible_text = page.locator("body").inner_text()

            return {
                "success": True,
                "status": "create_menu_inspected",
                "url": page.url,
                "menu_text": visible_text,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "inspect_failed",
                "error": str(exc),
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def click_upload_videos(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            upload_button = page.locator(
                "ytcp-icon-button#upload-icon"
            )

            if upload_button.count() == 0:
                return {
                    "success": False,
                    "status": "upload_icon_not_found",
                    "url": page.url,
                }

            upload_button.first.click(force=True)

            page.wait_for_timeout(3_000)

            return {
                "success": True,
                "status": "upload_icon_clicked",
                "url": page.url,
                "title": page.title(),
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "upload_icon_click_failed",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def inspect_upload_dialog(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                    "url": page.url,
                }

            create_button.first.click(force=True)
            page.wait_for_timeout(1_000)

            upload_button = page.get_by_text("Upload videos", exact=True)

            if upload_button.count() == 0:
                return {
                    "success": False,
                    "status": "upload_videos_not_found",
                    "url": page.url,
                }

            upload_button.first.click(force=True)
            page.wait_for_timeout(2_000)

            body_text = page.locator("body").inner_text()

            file_inputs = page.locator('input[type="file"]').count()

            return {
                "success": True,
                "status": "upload_dialog_inspected",
                "url": page.url,
                "file_input_count": file_inputs,
                "body_text": body_text[:5000],
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "upload_dialog_inspection_failed",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def inspect_upload_filechooser(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                }

            create_button.first.click(force=True)
            page.wait_for_timeout(1_000)

            upload_button = page.get_by_text(
                "Upload videos",
                exact=True,
            )

            if upload_button.count() == 0:
                return {
                    "success": False,
                    "status": "upload_videos_not_found",
                }

            with page.expect_file_chooser(timeout=10_000) as chooser_info:
                upload_button.first.click(force=True)

            chooser = chooser_info.value

            return {
                "success": True,
                "status": "filechooser_detected",
                "is_multiple": chooser.is_multiple,
                "url": page.url,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "filechooser_not_detected",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def inspect_upload_ui(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                }

            create_button.first.click(force=True)
            page.wait_for_timeout(1_000)

            upload_button = page.get_by_text(
                "Upload videos",
                exact=True,
            )

            if upload_button.count() == 0:
                return {
                    "success": False,
                    "status": "upload_videos_not_found",
                }

            upload_button.first.click(force=True)
            page.wait_for_timeout(2_000)

            dialogs = page.locator('[role="dialog"]')
            buttons = page.locator("button")
            inputs = page.locator("input")

            dialog_text = []
            for i in range(min(dialogs.count(), 10)):
                try:
                    dialog_text.append(dialogs.nth(i).inner_text())
                except Exception:
                    pass

            button_text = []
            for i in range(min(buttons.count(), 40)):
                try:
                    value = buttons.nth(i).inner_text().strip()
                    if value:
                        button_text.append(value)
                except Exception:
                    pass

            input_info = []
            for i in range(min(inputs.count(), 20)):
                try:
                    element = inputs.nth(i)
                    input_info.append({
                        "type": element.get_attribute("type"),
                        "accept": element.get_attribute("accept"),
                    })
                except Exception:
                    pass

            return {
                "success": True,
                "status": "upload_ui_inspected",
                "url": page.url,
                "dialogs": dialog_text,
                "buttons": button_text,
                "inputs": input_info,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "upload_ui_inspection_failed",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def diagnose_upload_click(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                }

            create_button.first.click(force=True)
            page.wait_for_timeout(1_000)

            upload_button = page.get_by_text(
                "Upload videos",
                exact=True,
            )

            if upload_button.count() == 0:
                return {
                    "success": False,
                    "status": "upload_videos_not_found",
                }

            before_url = page.url
            before_dialogs = page.locator('[role="dialog"]').count()

            upload_button.first.click(force=True)

            page.wait_for_timeout(5_000)

            after_url = page.url
            after_dialogs = page.locator('[role="dialog"]').count()
            body_text = page.locator("body").inner_text()

            return {
                "success": True,
                "status": "upload_click_diagnosed",
                "before_url": before_url,
                "after_url": after_url,
                "dialogs_before": before_dialogs,
                "dialogs_after": after_dialogs,
                "upload_text_visible": "Upload videos" in body_text,
                "body_excerpt": body_text[:3000],
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "upload_click_diagnosis_failed",
                "error": str(exc),
                "url": page.url,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def inspect_upload_element(self) -> dict[str, Any]:
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            create_button = page.get_by_text("Create", exact=True)

            if create_button.count() == 0:
                return {
                    "success": False,
                    "status": "create_button_not_found",
                }

            create_button.first.click(force=True)
            page.wait_for_timeout(1_000)

            upload = page.get_by_text(
                "Upload videos",
                exact=True,
            ).first

            if upload.count() == 0:
                return {
                    "success": False,
                    "status": "upload_videos_not_found",
                }

            result = []

            current = upload

            for level in range(5):
                try:
                    result.append({
                        "level": level,
                        "tag": current.evaluate(
                            "(el) => el.tagName"
                        ),
                        "class": current.get_attribute("class"),
                        "role": current.get_attribute("role"),
                        "aria_label": current.get_attribute(
                            "aria-label"
                        ),
                        "outer_html": current.evaluate(
                            "(el) => el.outerHTML"
                        )[:2000],
                    })

                    current = current.locator("..")

                except Exception as exc:
                    result.append({
                        "level": level,
                        "error": str(exc),
                    })
                    break

            return {
                "success": True,
                "status": "upload_element_inspected",
                "url": page.url,
                "ancestors": result,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "upload_element_inspection_failed",
                "error": str(exc),
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def is_logged_in(self) -> dict[str, Any]:
        playwright, context, page = self._start()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            current_url = page.url

            logged_in = (
                "accounts.google.com" not in current_url
                and "ServiceLogin" not in current_url
            )

            return {
                "success": True,
                "logged_in": logged_in,
                "url": current_url,
                "title": page.title(),
            }

        except Exception as exc:
            return {
                "success": False,
                "logged_in": False,
                "error": str(exc),
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def open_youtube_studio(self) -> dict[str, Any]:
        playwright, context, page = self._start()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            current_url = page.url

            if "accounts.google.com" in current_url:
                return {
                    "success": False,
                    "logged_in": False,
                    "status": "login_required",
                    "url": current_url,
                }

            return {
                "success": True,
                "logged_in": True,
                "status": "studio_open",
                "url": current_url,
                "title": page.title(),
            }

        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        thumbnail_path: str | None = None,
        publish: bool = False,
    ) -> dict[str, Any]:

        video = Path(video_path).resolve()

        if not video.exists():
            return {
                "success": False,
                "status": "video_not_found",
                "video_path": str(video),
            }

        playwright, context, page = self._start()

        try:
            page.goto(
                "https://studio.youtube.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            if "accounts.google.com" in page.url:
                return {
                    "success": False,
                    "logged_in": False,
                    "status": "login_required",
                    "url": page.url,
                }

            # Direct YouTube upload route.
            #
            # YouTube Studio currently exposes the upload action as
            # ytcp-icon-button#upload-icon. Clicking this icon creates
            # the hidden input[type="file"] used for the actual upload.
            upload_icon = page.locator(
                "ytcp-icon-button#upload-icon"
            )

            if upload_icon.count() == 0:
                return {
                    "success": False,
                    "status": "upload_icon_not_found",
                    "url": page.url,
                }

            if not upload_icon.first.is_visible():
                return {
                    "success": False,
                    "status": "upload_icon_not_visible",
                    "url": page.url,
                }

            if not upload_icon.first.is_enabled():
                return {
                    "success": False,
                    "status": "upload_icon_disabled",
                    "url": page.url,
                }

            upload_icon.first.click(force=True)

            page.wait_for_timeout(2_000)

            # Locate the hidden file input created by YouTube Studio.
            file_inputs = page.locator(
                'input[type="file"][name="Filedata"]'
            )

            if file_inputs.count() == 0:
                return {
                    "success": False,
                    "status": "youtube_file_input_not_found",
                    "url": page.url,
                }

            file_input = file_inputs.first

            file_input.set_input_files(str(video))

            page.wait_for_timeout(4_000)

            # Title.
            title_box = page.locator(
                '[contenteditable="true"][aria-label*="title that describes your video"]'
            ).first
    
            if title_box.count():
                title_box.fill(title)
    
            # Description.
            description_box = page.locator(
                '[contenteditable="true"][aria-label*="Tell viewers about your video"]'
            ).first
    
            if description_box.count():
                description_box.fill(description)
    
            # Thumbnail.
            if thumbnail_path:
                thumbnail = Path(thumbnail_path).resolve()
    
                if thumbnail.exists():
                    thumbnail_input = page.locator(
                        'input[type="file"]'
                    )
    
                    # Try to identify the thumbnail input by nearby
                    # UI rather than assuming a fixed index.
                    for i in range(thumbnail_input.count()):
                        try:
                            element = thumbnail_input.nth(i)
    
                            accept = element.get_attribute("accept")
    
                            if accept and "image" in accept:
                                element.set_input_files(
                                    str(thumbnail)
                                )
                                break
    
                        except Exception:
                            continue
    
    
            # Tags are intentionally handled later through the
            # advanced metadata layer. The first milestone is
            # reliable upload/title/description/publish.

            # Wait for upload processing.
            page.wait_for_timeout(5_000)

            if publish:

                # Look for the publish button.
                publish_button = page.get_by_text(
                    "Publish",
                    exact=True,
                )

                if publish_button.count() == 0:
                    return {
                        "success": False,
                        "status": "publish_button_not_found",
                        "url": page.url,
                    }

                publish_button.last.click()

                page.wait_for_timeout(5_000)

            return {
                "success": True,
                "status": "published" if publish else "uploaded",
                "video_path": str(video),
                "title": title,
                "url": page.url,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "browser_error",
                "error": str(exc),
                "url": page.url if not page.is_closed() else None,
            }

        finally:
            try:
                context.close()
            except Exception:
                pass

            try:
                playwright.stop()
            except Exception:
                pass

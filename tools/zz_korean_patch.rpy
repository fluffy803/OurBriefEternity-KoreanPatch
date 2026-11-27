# Korean patch for 永恒与星辰与日常 (Our Brief Eternity) — 11-20 build.
#
# The game now has its own localisation system (scripts/controls/localization.rpy):
# separate main / UI / text / voice languages, chosen on a language screen.
# Korean is added there as a fifth language:
#   text  -> tl/korean (dialogue and strings)
#   UI    -> obe_localization_catalog.UI["korean"] (zz_korean_ui.rpy, generated at build)
#            and tl/korean images
#   voice -> Japanese by default (there is no Korean dub)
# The first start after installing the patch switches the game to Korean once;
# after that the player's choice on the language screen is kept.

default persistent._ko_patch_language_set = False

init -19 python:
    import renpy.translation as _ko_tl

    L10N_LANGUAGES = L10N_LANGUAGES + ("korean",)
    L10N_NAMES["korean"] = "한국어"
    L10N_ART["korean"] = "kor"

    _l10n_localized_images["korean"] = set(
        _f.split("/", 2)[2] for _f in renpy.list_files()
        if _f.startswith(config.tl_directory + "/korean/")
        and _f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".avif")))

    _ko_base_default_voice = l10n_default_voice_language

    def l10n_default_voice_language(language):
        if language == "korean":
            return "japanese"
        return _ko_base_default_voice(language)

    _ko_base_linebreak = l10n_linebreak

    def l10n_linebreak(language=None):
        language = language or l10n_text_language()
        if language == "korean":
            return "korean-with-spaces"
        return _ko_base_linebreak(language)

    # Movies (images/*.webm) are played through the audio loader, so the engine looks
    # them up by *voice* language.  The Korean subtitled movies belong to the UI
    # language instead, otherwise Japanese voice would bring back the Chinese movies.
    _ko_base_language_for_file = _ko_tl.get_language_for_file

    def _ko_language_for_file(name=None, directory=None):
        if name and name.lower().endswith(".webm"):
            return _ko_tl.get_image_language()
        return _ko_base_language_for_file(name=name, directory=directory)

    _ko_tl.get_language_for_file = _ko_language_for_file

    def _ko_first_start():
        if persistent._ko_patch_language_set:
            return
        renpy.change_language("korean")
        _obe_translation.change_text_language("korean")
        _obe_translation.change_image_language("korean")
        _obe_translation.change_voice_language("japanese")
        persistent._obe_language_configured = True
        persistent._ko_patch_language_set = True
        renpy.save_persistent()

    config.start_callbacks.insert(config.start_callbacks.index(l10n_start), _ko_first_start)

# Four languages sit in a 2x2 grid; the fifth (Korean) goes to the right-hand cell of
# the third row, which is free in all three grids (the left cell of the main grid
# holds the "custom" indicator).
screen language_choices(category, left, top):
    for index, language in enumerate(L10N_LANGUAGES):
        $ button_art = "gui/localization/sys_data_language_bo1_" + L10N_ART[language]
        $ slot = 5 if index == 4 else index
        imagebutton:
            xpos left + (slot % 2) * 452
            ypos top + (slot // 2) * 109
            idle button_art + "_normal.png"
            hover button_art + "_click.png"
            selected_idle button_art + "_confim.png"
            selected_hover button_art + "_confim.png"
            activate_sound persistent.button_activate_sound
            hover_sound persistent.button_hover_sound
            action SetGameLanguage(language, category)

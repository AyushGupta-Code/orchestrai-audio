"""Structured planning service for Phase 5.

The planner is still rule-based, but it now produces a richer and more
predictable schema that looks more like an agent planning layer. The goal is
to hand downstream generation steps a cleaner, more expressive plan.
"""

from __future__ import annotations

from app.models.schemas import AudioRequest, AudioRequestPlan, SegmentPlan
from app.services.request_parser import extract_pomodoro_pattern, infer_mood_hint
from app.services.template_retrieval_service import enrich_plan_with_template


def build_audio_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Build a deterministic structured plan from the parsed request."""
    builders = {
        "music_session": build_music_plan,
        "pomodoro_session": build_pomodoro_plan,
        "audiobook": build_audiobook_plan,
        "ambient_session": build_ambient_plan,
        "custom_timeline": build_custom_timeline_plan,
    }
    plan = builders[audio_request.request_type](audio_request)
    return enrich_plan_with_template(plan)


def build_music_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Create one or more music-oriented segments."""
    mood = infer_mood(audio_request)
    style = infer_style(audio_request)
    pacing = infer_pacing(audio_request)
    segments: list[SegmentPlan] = []
    remaining_minutes = audio_request.total_duration_minutes
    segment_number = 1

    while remaining_minutes > 0:
        duration = min(30, remaining_minutes)
        segments.append(
            SegmentPlan(
                segment_id=f"segment-{segment_number:02d}",
                name=f"Music Block {segment_number}",
                segment_type="music",
                duration_minutes=duration,
                purpose="Sustain the music listening session.",
                mood=mood,
                style=style,
                music_prompt=build_music_prompt(audio_request.text, mood, style),
            )
        )
        remaining_minutes -= duration
        segment_number += 1

    return AudioRequestPlan(
        request_type=audio_request.request_type,
        title=audio_request.title,
        total_duration_minutes=audio_request.total_duration_minutes,
        mood=mood,
        style=style,
        pacing=pacing,
        needs_music=True,
        needs_narration=False,
        needs_breaks=False,
        break_pattern=None,
        output_strategy="layered_music_segments_then_stitch",
        segments=segments,
        notes=[
            "Structured planner created music blocks of up to 30 minutes each.",
            "Downstream generation should prioritize music continuity over voice cues.",
        ],
    )


def build_pomodoro_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Create repeated work and break blocks for a pomodoro request."""
    work_minutes, break_minutes = extract_pomodoro_pattern(audio_request.text)
    mood = infer_mood(audio_request)
    style = infer_style(audio_request)
    pacing = "steady"
    remaining_minutes = audio_request.total_duration_minutes
    segments: list[SegmentPlan] = []
    segment_number = 1
    cycle_number = 1

    while remaining_minutes > 0:
        current_work_minutes = min(work_minutes, remaining_minutes)
        segments.append(
            SegmentPlan(
                segment_id=f"segment-{segment_number:02d}",
                name=f"Focus Block {cycle_number}",
                segment_type="focus_block",
                duration_minutes=current_work_minutes,
                purpose="Hold the main work session for this pomodoro cycle.",
                mood=mood,
                style=style,
                music_prompt=f"{mood.title()} low-distraction background music for focus cycle {cycle_number} in a {style} style.",
                ambient_prompt="Soft neutral study ambience.",
                include_voice_cue=True,
            )
        )
        remaining_minutes -= current_work_minutes
        segment_number += 1

        if remaining_minutes <= 0:
            break

        current_break_minutes = min(break_minutes, remaining_minutes)
        segments.append(
            SegmentPlan(
                segment_id=f"segment-{segment_number:02d}",
                name=f"Break Block {cycle_number}",
                segment_type="break_block",
                duration_minutes=current_break_minutes,
                purpose="Provide a short break before the next focus block.",
                mood="gentle",
                style="reset",
                music_prompt="Gentle reset music for a short break.",
                narration_text="Take a short break, breathe, and reset for the next focus block.",
                include_voice_cue=True,
            )
        )
        remaining_minutes -= current_break_minutes
        segment_number += 1
        cycle_number += 1

    return AudioRequestPlan(
        request_type=audio_request.request_type,
        title=audio_request.title,
        total_duration_minutes=audio_request.total_duration_minutes,
        mood=mood,
        style=style,
        pacing=pacing,
        needs_music=True,
        needs_narration=True,
        needs_breaks=True,
        break_pattern=f"{work_minutes} minutes work / {break_minutes} minutes break",
        output_strategy="alternating_focus_and_break_segments",
        segments=segments,
        notes=[
            f"Work blocks use {work_minutes} minutes when possible.",
            f"Break blocks use {break_minutes} minutes when possible.",
            "Downstream generation should keep voice cues short and non-intrusive.",
        ],
    )


def build_audiobook_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Create a narration-focused structured plan for an audiobook request."""
    total_minutes = max(audio_request.total_duration_minutes, 10)
    narration_minutes = max(total_minutes - 4, 6)
    first_narration = narration_minutes // 2
    second_narration = narration_minutes - first_narration
    mood = infer_mood(audio_request)
    style = infer_style(audio_request)
    pacing = "measured"

    segments = [
        SegmentPlan(
            segment_id="segment-01",
            name="Audiobook Intro",
            segment_type="music",
            duration_minutes=1,
            purpose="Open the audiobook experience with a short theme.",
            mood=mood,
            style=style,
            music_prompt=f"Warm intro music with a {style} feel for an audiobook session.",
        ),
        SegmentPlan(
            segment_id="segment-02",
            name="Chapter Narration Part 1",
            segment_type="narration",
            duration_minutes=first_narration,
            purpose="Narrate the first half of the chapter.",
            mood=mood,
            style=style,
            music_prompt=f"Soft {mood} underscore for spoken narration in a {style} style.",
            narration_text=f"Stub narration for the first half of the request: {audio_request.text}",
            include_voice_cue=True,
        ),
        SegmentPlan(
            segment_id="segment-03",
            name="Music Interlude",
            segment_type="music",
            duration_minutes=2,
            purpose="Separate narration sections with a short transition.",
            mood="reflective",
            style=style,
            music_prompt="Short reflective music interlude between chapter sections.",
        ),
        SegmentPlan(
            segment_id="segment-04",
            name="Chapter Narration Part 2",
            segment_type="narration",
            duration_minutes=second_narration,
            purpose="Narrate the second half of the chapter.",
            mood=mood,
            style=style,
            music_prompt=f"Soft {mood} underscore for spoken narration in a {style} style.",
            narration_text="Stub narration for the second half of the chapter.",
            include_voice_cue=True,
        ),
        SegmentPlan(
            segment_id="segment-05",
            name="Audiobook Outro",
            segment_type="music",
            duration_minutes=1,
            purpose="Close the audiobook with a short outro theme.",
            mood="gentle",
            style=style,
            music_prompt="Gentle closing theme for an audiobook session.",
        ),
    ]

    return AudioRequestPlan(
        request_type=audio_request.request_type,
        title=audio_request.title,
        total_duration_minutes=total_minutes,
        mood=mood,
        style=style,
        pacing=pacing,
        needs_music=True,
        needs_narration=True,
        needs_breaks=False,
        break_pattern=None,
        output_strategy="narration_with_supporting_music_segments",
        segments=segments,
        notes=[
            "Audiobook plans use intro and outro music with two narration blocks.",
            "Downstream generation should keep narration intelligible over the background underscore.",
        ],
    )


def build_ambient_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Create long ambience blocks with a more structured ambient strategy."""
    mood = infer_mood(audio_request)
    style = infer_style(audio_request)
    pacing = "slow"
    segments: list[SegmentPlan] = []
    remaining_minutes = audio_request.total_duration_minutes
    segment_number = 1

    while remaining_minutes > 0:
        duration = min(60, remaining_minutes)
        segments.append(
            SegmentPlan(
                segment_id=f"segment-{segment_number:02d}",
                name=f"Ambient Block {segment_number}",
                segment_type="ambient",
                duration_minutes=duration,
                purpose="Maintain a continuous ambient environment.",
                mood=mood,
                style=style,
                ambient_prompt=f"{mood.title()} ambient soundscape for '{audio_request.text}' with a {style} texture.",
            )
        )
        remaining_minutes -= duration
        segment_number += 1

    return AudioRequestPlan(
        request_type=audio_request.request_type,
        title=audio_request.title,
        total_duration_minutes=audio_request.total_duration_minutes,
        mood=mood,
        style=style,
        pacing=pacing,
        needs_music=False,
        needs_narration=False,
        needs_breaks=False,
        break_pattern=None,
        output_strategy="long_form_ambient_layers",
        segments=segments,
        notes=[
            "Ambient plans use long blocks of up to 60 minutes each.",
            "Downstream generation should favor continuity and low variation between adjacent segments.",
        ],
    )


def build_custom_timeline_plan(audio_request: AudioRequest) -> AudioRequestPlan:
    """Create a structured multi-part timeline with intro, work, break, and outro."""
    total_minutes = max(audio_request.total_duration_minutes, 20)
    intro_minutes = 2
    break_minutes = 5
    outro_minutes = 3
    first_work_minutes = max((total_minutes - intro_minutes - break_minutes - outro_minutes) // 2, 5)
    second_work_minutes = max(total_minutes - intro_minutes - break_minutes - outro_minutes - first_work_minutes, 5)
    mood = infer_mood(audio_request)
    style = infer_style(audio_request)
    pacing = infer_pacing(audio_request)

    segments = [
        SegmentPlan(
            segment_id="segment-01",
            name="Intro",
            segment_type="intro",
            duration_minutes=intro_minutes,
            purpose="Open the custom timeline and set expectations.",
            mood="welcoming",
            style=style,
            music_prompt="Short opening music for a guided custom timeline.",
            narration_text="Welcome. The session is starting now.",
            include_voice_cue=True,
        ),
        SegmentPlan(
            segment_id="segment-02",
            name="Work Block 1",
            segment_type="work_block",
            duration_minutes=first_work_minutes,
            purpose="Run the first main work segment.",
            mood=mood,
            style=style,
            music_prompt=f"{mood.title()} background music for the first custom work block in a {style} style.",
        ),
        SegmentPlan(
            segment_id="segment-03",
            name="Break",
            segment_type="break_block",
            duration_minutes=break_minutes,
            purpose="Insert a short transition and recovery break.",
            mood="gentle",
            style="reset",
            music_prompt="Gentle transition music for a break.",
            narration_text="Take a short break before the next block.",
            include_voice_cue=True,
        ),
        SegmentPlan(
            segment_id="segment-04",
            name="Work Block 2",
            segment_type="work_block",
            duration_minutes=second_work_minutes,
            purpose="Run the second main work segment.",
            mood=mood,
            style=style,
            music_prompt=f"{mood.title()} background music for the second custom work block in a {style} style.",
        ),
        SegmentPlan(
            segment_id="segment-05",
            name="Outro",
            segment_type="outro",
            duration_minutes=outro_minutes,
            purpose="Close the session with a short ending.",
            mood="encouraging",
            style=style,
            music_prompt="Short closing music for a guided custom timeline.",
            narration_text="The session is complete. Nice work.",
            include_voice_cue=True,
        ),
    ]

    return AudioRequestPlan(
        request_type=audio_request.request_type,
        title=audio_request.title,
        total_duration_minutes=total_minutes,
        mood=mood,
        style=style,
        pacing=pacing,
        needs_music=True,
        needs_narration=True,
        needs_breaks=True,
        break_pattern="single mid-session break",
        output_strategy="guided_multi_part_timeline",
        segments=segments,
        notes=[
            "Custom timelines use a fixed beginner-friendly template in Phase 5.",
            "Downstream generation should preserve distinct transitions between intro, work, break, and outro.",
        ],
    )


def infer_mood(audio_request: AudioRequest) -> str:
    """Infer a stable mood label from obvious request keywords."""
    model_hint = infer_mood_hint(audio_request.text)
    if model_hint:
        return model_hint

    lower_text = audio_request.text.lower()
    if any(word in lower_text for word in ["calm", "rain", "ambient", "study", "gentle"]):
        return "calm"
    if any(word in lower_text for word in ["focus", "productivity", "pomodoro"]):
        return "focused"
    if any(word in lower_text for word in ["jazz", "energetic", "upbeat", "celebrate"]):
        return "energetic"
    if any(word in lower_text for word in ["chapter", "audiobook", "story"]):
        return "warm"
    return "balanced"


def infer_style(audio_request: AudioRequest) -> str:
    """Infer a simple style label that downstream services can reuse."""
    lower_text = audio_request.text.lower()
    if "jazz" in lower_text:
        return "jazz"
    if any(word in lower_text for word in ["rain", "ambient", "soundscape"]):
        return "ambient"
    if any(word in lower_text for word in ["audiobook", "chapter", "narration"]):
        return "cinematic"
    if any(word in lower_text for word in ["pomodoro", "focus", "study"]):
        return "minimal"
    return "hybrid"


def infer_pacing(audio_request: AudioRequest) -> str:
    """Infer a simple pacing label for the full session."""
    lower_text = audio_request.text.lower()
    if any(word in lower_text for word in ["calm", "ambient", "rain"]):
        return "slow"
    if any(word in lower_text for word in ["focus", "pomodoro", "study"]):
        return "steady"
    if any(word in lower_text for word in ["energetic", "upbeat", "celebrate"]):
        return "dynamic"
    return "moderate"


def build_music_prompt(request_text: str, mood: str, style: str) -> str:
    """Create a richer structured music prompt for downstream generation."""
    return f"{mood.title()} music in a {style} style based on request: {request_text}"

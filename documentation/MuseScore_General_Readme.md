# MuseScore_General.sf2

**Version 0.2.1**

---

Please see **MuseScore_General_License.md** for authorship and license information.

The purpose of this README is to provide useful information on instruments contained within MuseScore_General. It is currently a work-in-progress.

## About

This is a scaled-down version of **MuseScore_General-HQ.sf2** that replaces some of the larger instruments to save memory and CPU on older PCs. This SoundFont is currently a work-in-progress. Detailed information on presets and sample sources used can be found in "MuseScore_General_Sample_Sources.csv". All instruments without attribution are still using samples from FluidR3Mono.

## SoundFont Compatibility

**MuseScore_General** makes full use of SoundFont 2.01 specification modulators (particularly in the newer instruments) and requires a player/sampler with robust support for the standard. To my knowledge, the only SoundFont players that can accurately play this SoundFont are:

* [MuseScore](https://musescore.org)
* [FluidSynth](http://www.fluidsynth.org/)
* [Sobanth VSTi](https://blog.rosseaux.net/page/e5ca75d98990e33b31dadc78a8df1333/Sobanth)
* Sound Blaster Audigy/Audigy2 hardware SoundFont synth (probably X-Fi as well)

The only SoundFont editors that can play this SoundFont correctly are:

* Creative Vienna SoundFont Studio (requires Sound Blaster or E-MU hardware synth with SoundFont 2.01 modulator support)
* [SWAMI](http://www.swamiproject.org/) (uses FluidSynth)

## Presets

### General MIDI Presets

**MuseScore_General** is compatible with the [General MIDI standard](https://en.wikipedia.org/wiki/General_MIDI) with some additional presets from the [Roland GS standard](https://en.wikipedia.org/wiki/Roland_GS) as well.

### Fluid r3 Additional Drum Kits

Additional drum kits have been inherited from **Fluid r3**, beyond the kits specified in the [Roland GS standard](https://en.wikipedia.org/wiki/Roland_GS). It is possible that some of these kits will be removed in the future when new drum samples are added.

### Instrument Variations

In addition to the General MIDI presets, further instrument variations can be found on banks 20 and above, utilizing identical preset numbers so that General MIDI preset fallback can occur if ever the instrument becomes no longer available on the higher bank number. In other words, if you have a track assigned to bank #40, preset #48 "Celli Fast", then try to play it using a different General MIDI device or SoundFont, the preset will fall back to bank #0, preset #48 "Fast Strings" instead, and playback will at least sound somewhat correct.

### MuseScore Marching Percussion

The following marching percussion presets exist in the percussion bank (bank 128):
* 56: Marching Snare
* 57: OldMarchingBass
* 58: Marching Cymbals
* 59: Marching Bass
* 95: OldMarchingTenor
* 96: Marching Tenor

These presets are used for marching percussion support in MuseScore and do not conform to GM layout.

### Expressive Presets

As of version 0.1.5, **MuseScore_General** features expressive variants of all sustained presets, indicated by "Expr." at the end of the preset name. The dynamics of these presets are controlled using MIDI Control Change #2 (CC2), allowing fluid crescendos and diminuendos while a note is being held. This makes for much more realistic expression of strings, brass, woodwinds, etc. Note velocity no longer controls dynamics in these presets, but in some instruments, velocity will have some effect on the speed of the note attack. In MuseScore, the default (and ideal) behavior is for expressive instruments to have their dynamics controlled by sending identical values to both CC2 and note velocity (the latter only during note-on, naturally).

The expressive presets exist on higher bank numbers but use the same preset number as their non-expressive defaults. You can see what bank numbers the expressive presets use in column #2 ("Expr. Bank #") of the included **MuseScore_General_Sample_Sources.csv** file. The general rule is as follows:

* Bank 0 expressive presets are on Bank 17
* Bank 8 expressive presets are on Bank 18
* Bank 20-126 expressive presets are one bank higher (e.g., Bank 20 Expr. presets are on Bank 21)

### Dummy Presets

To maintain preset compatibility with the "HQ" version, **MuseScore_General** version contains dummy presets that are simply duplicates of the similar instruments found on bank 0. For example, the full SoundFont has the following instruments assigned to preset #48, all on different banks (presets listed in bank#:preset# format):

- 000:048 - Strings Fast
- 020:048 - Violins Fast
- 025:048 - Violins2 Fast
- 030:048 - Violas Fast
- 040:048 - Celli Fast
- 050:048 - Basses Fast

In the HQ version of the SoundFont, each of these sounds different since they feature unique samples for each section, but in this **MuseScore_General**, these presets on banks 20 and higher are mere duplicates of **000:048 - Strings Fast**, and only exist to avoid issues transitioning between the HQ and lighter versions of the SoundFont.

All dummy presets are indicated as such in the included **MuseScore_General_Sample_Sources.csv** file.

### Metronome Clicks

This SoundFont includes two pairs of metronome clicks that can be used for “counting in” and/or a “click track”; see [#154666](https://musescore.org/en/node/154666) for some background story.

#### MDL Metronome

This is the metronome sound from MuseScore Drumline, synthesized by S. Christian Collins to resemble the sound of the BOSS DB-90 metronome, which is commonly used in drumline percussion.

- emphasis click: note A♯₁ (MIDI note 34, percussion (General MIDI 2 drums) Metronome Bell)
- normal click: note A₁ (MIDI note 33, percussion (General MIDI 2 drums) Metronome Click)

There is no default percussion staff type set up for this metronome in MuseScore, but the sounds do have an appropriate MIDI fallback. It can be used, for example with a temporary mid-stave instrument change, in any pitched instrument staff though.

#### Ardour Metronome

This is the metronome sound built into MuseScore and used when its count-in and/or metronome functionality is used. These were created by Paul Davis, originally for Ardour, by generating them following a mathematical formula, so they are not original and therefore not protected by copyright.

- emphasis click: note E₅ (MIDI note 76, percussion (MuseScore) High Woodblock)
- normal click: note F₅ (MIDI note 77, percussion (MuseScore) Low Woodblock)

This metronome can easily be used by a (possibly temporary) mid-stave instrument change with any pitched instrument; furthermore, a percussion stave is already set up for it as MuseScore instrument Wood Blocks. Keep the volume at or near 100, which is close to what MuseScore uses for its built-in metronome.

Incidentally (see the example picture below), the MIDI note number of the emphasis pitch is **lower** than the one of the normal pitch. Do not let this fool you; this setup stems from the General MIDI drum map for Wood Blocks. Note that, in the percussion stave, the High Woodblock *is* displayed above the Low Woodblock.

#### How to use the Metronome sounds

Each of these pairs has an “emphasis” and a “normal” click. They are used, with varying velocities, for different types of beats; MuseScore uses them as follows:

| beat type        | click    | velocity | colour (in the picture below) |
| ----------------:| --------:| --------:| ----------------------------- |
| downbeat         | emphasis |      127 | green                         |
| stressed         | normal   |      127 | red                           |
| unstressed       | normal   |       80 | blue                          |
| compound subbeat | normal   |       25 | (not present)                 |
| other subbeat    | normal   |       15 | (not present)                 |

In the following example picture, the use of the Ardour Metronome is shown in a common time signature:

![Example showing the Metronome sounds](images/Metronom.png)

This is how you would enter this in MuseScore:

- Assign the Metronome sound to a staff, either permanently or using a mid-stave instrument change:
  - Patch 010:115 “Metronome” as ordinary instrument
  - Patch 128:055 “Metronome” as drumset
- Enter the clicks (emphasis or normal) on every beat
  - Enter E₅/F₅ or A♯₁/A₁ when in a melodic instrument
  - Enter High/Low Woodblock (Ardour metronome only) for percussion
- Select all metronome notes, open the mu͒ Inspector (F8 key)
  - Change Velocity type to “User”
  - Set Velocity, for all notes at first, to 127
- Select the metronome notes for unstressed beats only
  - Change Velocity to 80
- If you have any subbeats, select only them and apply the correct velocity

In a DAW, do the same, but you can probably enter by MIDI note number there.

For other time signatures or measure divisions (such as dividing a four-quarter time into dotted-quarter + dotted-quarter + quarter), use the respective appropriate beat stress pattern.

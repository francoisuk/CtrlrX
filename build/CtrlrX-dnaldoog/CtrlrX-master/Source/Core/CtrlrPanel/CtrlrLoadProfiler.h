#pragma once

/*
    TEMPORARY load-phase instrumentation for the large-panel investigation.
    Background: investigations/large-panel-perf/LARGE_PANEL_LOAD_REPORT.md §8.

    This file adds MEASUREMENT ONLY. It changes no logic and no control flow.

    Call sites (five markers):
        CtrlrPanelFileOperations.cpp : t0 at openXmlPanel entry, t1 after fromXml
        CtrlrPanel.cpp               : t2 after Lua restore, t3 after resource
                                       import, t4 after editor restore + report

    To remove everything: set CTRLR_LOAD_PROFILING to 0 below (every call site
    compiles away), or delete this header together with the five call sites.
*/

#ifndef CTRLR_LOAD_PROFILING
    #define CTRLR_LOAD_PROFILING 1
#endif

#if CTRLR_LOAD_PROFILING

#include <juce_core/juce_core.h>

#if JUCE_WINDOWS
    #ifndef NOMINMAX
        #define NOMINMAX
    #endif
    #ifndef WIN32_LEAN_AND_MEAN
        #define WIN32_LEAN_AND_MEAN
    #endif
    #include <windows.h>
    #include <psapi.h>
#elif JUCE_MAC || JUCE_LINUX
    #include <sys/resource.h>
#endif

namespace ctrlrLoadProfiler
{
    struct Marks
    {
        double t0 = -1.0;
        double t1 = -1.0;
        double t2 = -1.0;
        double t3 = -1.0;
        double t4 = -1.0;
        juce::String panelPath;
    };

    inline Marks& marks()
    {
        static Marks m;
        return m;
    }

    // Sub-millisecond resolution; getMillisecondCounter() would quantise the
    // smaller phases to whole milliseconds.
    inline double nowMs()
    {
        return juce::Time::getMillisecondCounterHiRes();
    }

    // Proves how far the load got when the final report never appears: each
    // marker appends one short line. A few microseconds per call.
    inline void trace (const char* what, double t)
    {
        juce::File f = juce::File::getSpecialLocation (juce::File::tempDirectory)
                           .getChildFile ("ctrlr_load_trace.txt");

        f.appendText (juce::String (t, 2) + " ms  " + what + "\n");
    }

    inline void begin (const juce::String& panelPath)
    {
        auto& m = marks();
        m = Marks();
        m.t0 = nowMs();
        m.panelPath = panelPath;

        juce::File::getSpecialLocation (juce::File::tempDirectory)
            .getChildFile ("ctrlr_load_trace.txt")
            .replaceWithText ("t0 openXmlPanel entered: " + panelPath + "\n" + juce::String (m.t0, 2) + " ms\n");
    }

    inline void mark (const int which)
    {
        auto& m = marks();
        const double t = nowMs();

        switch (which)
        {
            case 1: m.t1 = t; trace ("t1 after fromXml", t); break;
            case 2: m.t2 = t; trace ("t2 after lua restore", t); break;
            case 3: m.t3 = t; trace ("t3 after resource import", t); break;
            case 4: m.t4 = t; trace ("t4 after editor restore", t); break;
            default: break;
        }
    }

    inline juce::int64 peakRssBytes()
    {
    #if JUCE_WINDOWS
        // Resolved at run time so that no additional import library is needed
        // (psapi.lib is not linked by this project).
        typedef BOOL (WINAPI* GetProcessMemoryInfoFn) (HANDLE, PROCESS_MEMORY_COUNTERS*, DWORD);

        static GetProcessMemoryInfoFn fn = []
        {
            if (HMODULE k32 = GetModuleHandleW (L"kernel32.dll"))
                return reinterpret_cast<GetProcessMemoryInfoFn> (GetProcAddress (k32, "K32GetProcessMemoryInfo"));

            return (GetProcessMemoryInfoFn) nullptr;
        }();

        if (fn != nullptr)
        {
            PROCESS_MEMORY_COUNTERS_EX pmc {};
            if (fn (GetCurrentProcess(), reinterpret_cast<PROCESS_MEMORY_COUNTERS*> (&pmc), sizeof (pmc)))
                return (juce::int64) pmc.PeakWorkingSetSize;
        }

        return -1;
    #elif JUCE_MAC || JUCE_LINUX
        struct rusage ru {};
        if (getrusage (RUSAGE_SELF, &ru) == 0)
        {
        #if JUCE_MAC
            return (juce::int64) ru.ru_maxrss;          // bytes on macOS
        #else
            return (juce::int64) ru.ru_maxrss * 1024;   // KiB on Linux
        #endif
        }

        return -1;
    #else
        return -1;
    #endif
    }

    inline juce::String report()
    {
        auto& m = marks();
        const juce::int64 peak = peakRssBytes();

        auto delta = [&] (double a, double b) -> juce::String
        {
            if (a < 0.0 || b < 0.0)
                return juce::String ("n/a");

            return juce::String (b - a, 2) + " ms";
        };

        juce::String s;
        s << "\n";
        s << "==================== CTRLR LOAD PROFILE ====================\n";
        s << "panel               : "
          << (m.panelPath.isEmpty() ? juce::String ("(not loaded from a file)") : m.panelPath) << "\n";
        s << "------------------------------------------------------------\n";
        s << "XML Parse           (t1 - t0) : " << delta (m.t0, m.t1) << "\n";
        s << "Lua Execute         (t2 - t1) : " << delta (m.t1, m.t2) << "\n";
        s << "Resource Import     (t3 - t2) : " << delta (m.t2, m.t3) << "\n";
        s << "Widget Construction (t4 - t3) : " << delta (m.t3, m.t4) << "\n";
        s << "Total Load          (t4 - t0) : " << delta (m.t0, m.t4) << "\n";
        s << "------------------------------------------------------------\n";

        if (peak >= 0)
            s << "Peak RSS                      : " << juce::String ((double) peak / (1024.0 * 1024.0), 1) << " MB\n";
        else
            s << "Peak RSS                      : unavailable\n";

        s << "------------------------------------------------------------\n";
        s << "note: t3 is taken after the resource import chain (the\n";
        s << "      resourceExportList / instance / missing-resources\n";
        s << "      branches). t3..t4 therefore also contains the\n";
        s << "      luaPanelBeforeLoad callback, resourceManager.\n";
        s << "      restoreSavedState, setSavePoint, the editor restore\n";
        s << "      itself, window-manager restore and custom data.\n";
        s << "============================================================\n";

        return s;
    }

    inline void writeReport()
    {
        const juce::String block = report();

        juce::Logger::writeToLog (block);

    #if JUCE_WINDOWS
        ::OutputDebugStringW (block.toWideCharPointer());
    #endif

        // Written unconditionally: a packaged GUI executable has no console,
        // so this file is the reliable channel.
        juce::File::getSpecialLocation (juce::File::tempDirectory)
            .getChildFile ("ctrlr_load_profile.txt")
            .replaceWithText (block, false, false, "\n");
    }
}

    #define CTRLR_PROF_BEGIN(path) ctrlrLoadProfiler::begin (path)
    #define CTRLR_PROF_MARK(n)     ctrlrLoadProfiler::mark (n)
    #define CTRLR_PROF_REPORT()    ctrlrLoadProfiler::writeReport()
    #define CTRLR_PROF_TRACE(msg)  ctrlrLoadProfiler::trace (msg, ctrlrLoadProfiler::nowMs())

#else

    #define CTRLR_PROF_BEGIN(path) do {} while (false)
    #define CTRLR_PROF_MARK(n)     do {} while (false)
    #define CTRLR_PROF_REPORT()    do {} while (false)
    #define CTRLR_PROF_TRACE(msg)  do {} while (false)

#endif

/*
  ==============================================================================

   This file is part of the JUCE framework.
   Copyright (c) Raw Material Software Limited

   JUCE is an open source framework subject to commercial or open source
   licensing.

   By downloading, installing, or using the JUCE framework, or combining the
   JUCE framework with any other source code, object code, content or any other
   copyrightable work, you agree to the terms of the JUCE End User Licence
   Agreement, and all incorporated terms including the JUCE Privacy Policy and
   the JUCE Website Terms of Service, as applicable, which will bind you. If you
   do not agree to the terms of these agreements, we will not license the JUCE
   framework to you, and you must discontinue the installation or download
   process and cease use of the JUCE framework.

   JUCE End User Licence Agreement: https://juce.com/legal/juce-8-licence/
   JUCE Privacy Policy: https://juce.com/juce-privacy-policy
   JUCE Website Terms of Service: https://juce.com/juce-website-terms-of-service/

   Or:

   You may also use this code under the terms of the AGPLv3:
   https://www.gnu.org/licenses/agpl-3.0.en.html

   THE JUCE FRAMEWORK IS PROVIDED "AS IS" WITHOUT ANY WARRANTY, AND ALL
   WARRANTIES, WHETHER EXPRESSED OR IMPLIED, INCLUDING WARRANTY OF
   MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, ARE DISCLAIMED.

  ==============================================================================
*/

namespace juce
{

// ===================== TEMPORARY XML PARSE PROFILING =====================
// Measurement only. No parsing behaviour, control flow or signatures change.
// Set JUCE_XML_PARSE_PROFILE to 0, or delete this block plus the four marked
// call sites (search for "XMLParseProfile"), to compile it all out.
#ifndef JUCE_XML_PARSE_PROFILE
 #define JUCE_XML_PARSE_PROFILE 1
#endif

#if JUCE_XML_PARSE_PROFILE
namespace XmlParseProfile
{
    struct Totals
    {
        int64 totalTicks   = 0;
        int64 quotedTicks  = 0;   // sum of whole readQuotedString() calls
        int64 entityTicks  = 0;   // readEntity() calls made from inside those
        int64 quotedCalls  = 0;
        int64 entityCalls  = 0;
        int64 attrBytes    = 0;
        int64 elements     = 0;
    };

    inline Totals& totals() { static Totals t; return t; }

    inline int64 nowTicks() noexcept { return Time::getHighResolutionTicks(); }

    inline double ms (int64 ticks) noexcept
    {
        return Time::highResolutionTicksToSeconds (ticks) * 1000.0;
    }

    struct QuotedTimer
    {
        QuotedTimer() : start (nowTicks()) {}
        ~QuotedTimer()
        {
            totals().quotedTicks += nowTicks() - start;
            ++totals().quotedCalls;
        }
        int64 start;
    };

    struct EntityTimer
    {
        EntityTimer() : start (nowTicks()) {}
        ~EntityTimer()
        {
            totals().entityTicks += nowTicks() - start;
            ++totals().entityCalls;
        }
        int64 start;
    };

    inline void dump()
    {
        auto& t = totals();

        // Only report parses slow enough to matter, so that a later small
        // document (settings, presets) cannot overwrite the interesting result.
        if (ms (t.totalTicks) < 100.0)
            return;

        String s;
        s << "=== JUCE XmlDocument::parse profile ===\n";
        s << "total                    : " << String (ms (t.totalTicks), 2) << " ms\n";
        s << "attribute values         : " << String (ms (t.quotedTicks), 2) << " ms   ("
          << t.quotedCalls << " calls, " << String ((double) t.attrBytes / (1024.0 * 1024.0), 1) << " MB)\n";
        s << "   of which entity decode: " << String (ms (t.entityTicks), 2) << " ms   ("
          << t.entityCalls << " entities)\n";
        s << "   attribute text only   : " << String (ms (t.quotedTicks - t.entityTicks), 2) << " ms\n";
        s << "structural (everything else): "
          << String (ms (t.totalTicks - t.quotedTicks), 2) << " ms\n";
        s << "elements                 : " << t.elements << "\n";

        Logger::writeToLog (s);

        File::getSpecialLocation (File::tempDirectory)
            .getChildFile ("juce_xml_parse_profile.txt")
            .replaceWithText (s, false, false, "\n");
    }
}
#endif
// =================== end temporary XML parse profiling ===================

XmlDocument::XmlDocument (const String& text)  : originalText (text) {}
XmlDocument::XmlDocument (const File& file)  : inputSource (new FileInputSource (file)) {}

XmlDocument::~XmlDocument() {}

std::unique_ptr<XmlElement> XmlDocument::parse (const File& file)
{
    return XmlDocument (file).getDocumentElement();
}

std::unique_ptr<XmlElement> XmlDocument::parse (const String& textToParse)
{
    return XmlDocument (textToParse).getDocumentElement();
}

std::unique_ptr<XmlElement> parseXML (const String& textToParse)
{
    return XmlDocument (textToParse).getDocumentElement();
}

std::unique_ptr<XmlElement> parseXML (const File& file)
{
    return XmlDocument (file).getDocumentElement();
}

std::unique_ptr<XmlElement> parseXMLIfTagMatches (const String& textToParse, StringRef requiredTag)
{
    return XmlDocument (textToParse).getDocumentElementIfTagMatches (requiredTag);
}

std::unique_ptr<XmlElement> parseXMLIfTagMatches (const File& file, StringRef requiredTag)
{
    return XmlDocument (file).getDocumentElementIfTagMatches (requiredTag);
}

void XmlDocument::setInputSource (InputSource* newSource) noexcept
{
    inputSource.reset (newSource);
}

void XmlDocument::setEmptyTextElementsIgnored (bool shouldBeIgnored) noexcept
{
    ignoreEmptyTextElements = shouldBeIgnored;
}

namespace XmlIdentifierChars
{
    static bool isIdentifierCharSlow (juce_wchar c) noexcept
    {
        return CharacterFunctions::isLetterOrDigit (c)
                 || c == '_' || c == '-' || c == ':' || c == '.';
    }

    static bool isIdentifierChar (juce_wchar c) noexcept
    {
        static const uint32 legalChars[] = { 0, 0x7ff6000, 0x87fffffe, 0x7fffffe, 0 };

        return ((int) c < (int) numElementsInArray (legalChars) * 32) ? ((legalChars [c >> 5] & (uint32) (1 << (c & 31))) != 0)
                                                                      : isIdentifierCharSlow (c);
    }

    /*static void generateIdentifierCharConstants()
    {
        uint32 n[8] = { 0 };
        for (int i = 0; i < 256; ++i)
            if (isIdentifierCharSlow (i))
                n[i >> 5] |= (1 << (i & 31));

        String s;
        for (int i = 0; i < 8; ++i)
            s << "0x" << String::toHexString ((int) n[i]) << ", ";

        DBG (s);
    }*/

    static String::CharPointerType findEndOfToken (String::CharPointerType p) noexcept
    {
        while (isIdentifierChar (*p))
            ++p;

        return p;
    }
}

std::unique_ptr<XmlElement> XmlDocument::getDocumentElement (const bool onlyReadOuterDocumentElement)
{
    if (originalText.isEmpty() && inputSource != nullptr)
    {
        std::unique_ptr<InputStream> in (inputSource->createInputStream());

        if (in != nullptr)
        {
            MemoryOutputStream data;
            data.writeFromInputStream (*in, onlyReadOuterDocumentElement ? 8192 : -1);

           #if JUCE_STRING_UTF_TYPE == 8
            if (data.getDataSize() > 2)
            {
                data.writeByte (0);
                auto* text = static_cast<const char*> (data.getData());

                if (CharPointer_UTF16::isByteOrderMarkBigEndian (text)
                      || CharPointer_UTF16::isByteOrderMarkLittleEndian (text))
                {
                    originalText = data.toString();
                }
                else
                {
                    if (CharPointer_UTF8::isByteOrderMark (text))
                        text += 3;

                    // parse the input buffer directly to avoid copying it all to a string
                    return parseDocumentElement (String::CharPointerType (text), onlyReadOuterDocumentElement);
                }
            }
           #else
            originalText = data.toString();
           #endif
        }
    }

    return parseDocumentElement (originalText.getCharPointer(), onlyReadOuterDocumentElement);
}

std::unique_ptr<XmlElement> XmlDocument::getDocumentElementIfTagMatches (StringRef requiredTag)
{
    if (auto xml = getDocumentElement (true))
        if (xml->hasTagName (requiredTag))
            return getDocumentElement (false);

    return {};
}

const String& XmlDocument::getLastParseError() const noexcept
{
    return lastError;
}

void XmlDocument::setLastError (const String& desc, const bool carryOn)
{
    lastError = desc;
    errorOccurred = ! carryOn;
}

String XmlDocument::getFileContents (const String& filename) const
{
    if (inputSource != nullptr)
    {
        std::unique_ptr<InputStream> in (inputSource->createInputStreamFor (filename.trim().unquoted()));

        if (in != nullptr)
            return in->readEntireStreamAsString();
    }

    return {};
}

juce_wchar XmlDocument::readNextChar() noexcept
{
    auto c = input.getAndAdvance();

    if (c == 0)
    {
        outOfData = true;
        --input;
    }

    return c;
}

std::unique_ptr<XmlElement> XmlDocument::parseDocumentElement (String::CharPointerType textToParse,
                                                               bool onlyReadOuterDocumentElement)
{
    input = textToParse;
    errorOccurred = false;
    outOfData = false;
    needToLoadDTD = true;

   #if JUCE_XML_PARSE_PROFILE // XMLParseProfile: whole-parse scope + dump
    XmlParseProfile::totals() = XmlParseProfile::Totals();
    struct ProfileScope
    {
        int64 t0;
        ~ProfileScope()
        {
            XmlParseProfile::totals().totalTicks = XmlParseProfile::nowTicks() - t0;
            XmlParseProfile::dump();
        }
    } profileScope { XmlParseProfile::nowTicks() };
   #endif

    if (textToParse.isEmpty())
    {
        lastError = "not enough input";
    }
    else if (! parseHeader())
    {
        lastError = "malformed header";
    }
    else if (! parseDTD())
    {
        lastError = "malformed DTD";
    }
    else
    {
        lastError.clear();
        std::unique_ptr<XmlElement> result (readNextElement (! onlyReadOuterDocumentElement));

        if (! errorOccurred)
            return result;
    }

    return {};
}

bool XmlDocument::parseHeader()
{
    skipNextWhiteSpace();

    if (CharacterFunctions::compareUpTo (input, CharPointer_ASCII ("<?xml"), 5) == 0)
    {
        auto headerEnd = CharacterFunctions::find (input, CharPointer_ASCII ("?>"));

        if (headerEnd.isEmpty())
            return false;

       #if JUCE_DEBUG
        auto encoding = String (input, headerEnd)
                          .fromFirstOccurrenceOf ("encoding", false, true)
                          .fromFirstOccurrenceOf ("=", false, false)
                          .fromFirstOccurrenceOf ("\"", false, false)
                          .upToFirstOccurrenceOf ("\"", false, false)
                          .trim();

        /* If you load an XML document with a non-UTF encoding type, it may have been
           loaded wrongly. Since all the files are read via the normal juce file streams,
           they're treated as UTF-8, so by the time it gets to the parser, the encoding will
           have been lost. Best plan is to stick to utf-8 or if you have specific files to
           read, use your own code to convert them to a unicode String, and pass that to the
           XML parser.
        */
        jassert (encoding.isEmpty() || encoding.startsWithIgnoreCase ("utf-"));
       #endif

        input = headerEnd + 2;
        skipNextWhiteSpace();
    }

    return true;
}

bool XmlDocument::parseDTD()
{
    if (CharacterFunctions::compareUpTo (input, CharPointer_ASCII ("<!DOCTYPE"), 9) == 0)
    {
        input += 9;
        auto dtdStart = input;

        for (int n = 1; n > 0;)
        {
            auto c = readNextChar();

            if (outOfData)
                return false;

            if (c == '<')
                ++n;
            else if (c == '>')
                --n;
        }

        dtdText = String (dtdStart, input - 1).trim();
    }

    return true;
}

void XmlDocument::skipNextWhiteSpace()
{
    for (;;)
    {
        input.incrementToEndOfWhitespace();

        if (input.isEmpty())
        {
            outOfData = true;
            break;
        }

        if (*input == '<')
        {
            if (input[1] == '!'
                 && input[2] == '-'
                 && input[3] == '-')
            {
                input += 4;
                auto closeComment = input.indexOf (CharPointer_ASCII ("-->"));

                if (closeComment < 0)
                {
                    outOfData = true;
                    break;
                }

                input += closeComment + 3;
                continue;
            }

            if (input[1] == '?')
            {
                input += 2;
                auto closeBracket = input.indexOf (CharPointer_ASCII ("?>"));

                if (closeBracket < 0)
                {
                    outOfData = true;
                    break;
                }

                input += closeBracket + 2;
                continue;
            }
        }

        break;
    }
}

void XmlDocument::readQuotedString (String& result)
{
    auto quote = readNextChar();

    while (! outOfData)
    {
        auto c = readNextChar();

        if (c == quote)
            break;

        --input;

        if (c == '&')
        {
           #if JUCE_XML_PARSE_PROFILE // XMLParseProfile: entity decode
            XmlParseProfile::EntityTimer entityTimer;
           #endif
            readEntity (result);
        }
        else
        {
            auto start = input;

            for (;;)
            {
                auto character = *input;

                if (character == quote)
                {
                    result.appendCharPointer (start, input);
                    ++input;
                    return;
                }

                if (character == '&')
                {
                    result.appendCharPointer (start, input);
                    break;
                }

                if (character == 0)
                {
                    setLastError ("unmatched quotes", false);
                    outOfData = true;
                    break;
                }

                ++input;
            }
        }
    }
}

XmlElement* XmlDocument::readNextElement (const bool alsoParseSubElements)
{
    XmlElement* node = nullptr;
    skipNextWhiteSpace();

    if (outOfData)
        return nullptr;

    if (*input == '<')
    {
        ++input;
        auto endOfToken = XmlIdentifierChars::findEndOfToken (input);

        if (endOfToken == input)
        {
            // no tag name - but allow for a gap after the '<' before giving an error
            skipNextWhiteSpace();
            endOfToken = XmlIdentifierChars::findEndOfToken (input);

            if (endOfToken == input)
            {
                setLastError ("tag name missing", false);
                return node;
            }
        }

        node = new XmlElement (input, endOfToken);
       #if JUCE_XML_PARSE_PROFILE // XMLParseProfile: element counter
        ++XmlParseProfile::totals().elements;
       #endif
        input = endOfToken;
        LinkedListPointer<XmlElement::XmlAttributeNode>::Appender attributeAppender (node->attributes);

        // look for attributes
        for (;;)
        {
            skipNextWhiteSpace();
            auto c = *input;

            // empty tag
            if (c == '/' && input[1] == '>')
            {
                input += 2;
                break;
            }

            // parse the guts of the element
            if (c == '>')
            {
                ++input;

                if (alsoParseSubElements)
                    readChildElements (*node);

                break;
            }

            // get an attribute
            if (XmlIdentifierChars::isIdentifierChar (c))
            {
                auto attNameEnd = XmlIdentifierChars::findEndOfToken (input);

                if (attNameEnd != input)
                {
                    auto attNameStart = input;
                    input = attNameEnd;
                    skipNextWhiteSpace();

                    if (readNextChar() == '=')
                    {
                        skipNextWhiteSpace();
                        auto nextChar = *input;

                        if (nextChar == '"' || nextChar == '\'')
                        {
                            auto* newAtt = new XmlElement::XmlAttributeNode (attNameStart, attNameEnd);
                           #if JUCE_XML_PARSE_PROFILE // XMLParseProfile: attribute value extraction
                            {
                                XmlParseProfile::QuotedTimer quotedTimer;
                                readQuotedString (newAtt->attribute.value);
                            }
                            XmlParseProfile::totals().attrBytes += newAtt->attribute.value.length();
                           #else
                            readQuotedString (newAtt->attribute.value);
                           #endif
                            attributeAppender.append (newAtt);
                            continue;
                        }
                    }
                    else
                    {
                        setLastError ("expected '=' after attribute '"
                                        + String (attNameStart, attNameEnd) + "'", false);
                        return node;
                    }
                }
            }
            else
            {
                if (! outOfData)
                    setLastError ("illegal character found in " + node->getTagName() + ": '" + c + "'", false);
            }

            break;
        }
    }

    return node;
}

void XmlDocument::readChildElements (XmlElement& parent)
{
    LinkedListPointer<XmlElement>::Appender childAppender (parent.firstChildElement);

    for (;;)
    {
        auto preWhitespaceInput = input;
        skipNextWhiteSpace();

        if (outOfData)
        {
            setLastError ("unmatched tags", false);
            break;
        }

        if (*input == '<')
        {
            auto c1 = input[1];

            if (c1 == '/')
            {
                // our close tag
                auto closeTag = input.indexOf ((juce_wchar) '>');

                if (closeTag >= 0)
                    input += closeTag + 1;

                break;
            }

            if (c1 == '!' && CharacterFunctions::compareUpTo (input + 2, CharPointer_ASCII ("[CDATA["), 7) == 0)
            {
                input += 9;
                auto inputStart = input;

                for (;;)
                {
                    auto c0 = *input;

                    if (c0 == 0)
                    {
                        setLastError ("unterminated CDATA section", false);
                        outOfData = true;
                        break;
                    }

                    if (c0 == ']' && input[1] == ']' && input[2] == '>')
                    {
                        childAppender.append (XmlElement::createTextElement (String (inputStart, input)));
                        input += 3;
                        break;
                    }

                    ++input;
                }
            }
            else
            {
                // this is some other element, so parse and add it
                if (auto* n = readNextElement (true))
                    childAppender.append (n);
                else
                    break;
            }
        }
        else  // must be a character block
        {
            input = preWhitespaceInput; // roll back to include the leading whitespace
            MemoryOutputStream textElementContent;
            bool contentShouldBeUsed = ! ignoreEmptyTextElements;

            for (;;)
            {
                auto c = *input;

                if (c == '<')
                {
                    if (input[1] == '!' && input[2] == '-' && input[3] == '-')
                    {
                        input += 4;
                        auto closeComment = input.indexOf (CharPointer_ASCII ("-->"));

                        if (closeComment < 0)
                        {
                            setLastError ("unterminated comment", false);
                            outOfData = true;
                            return;
                        }

                        input += closeComment + 3;
                        continue;
                    }

                    break;
                }

                if (c == 0)
                {
                    setLastError ("unmatched tags", false);
                    outOfData = true;
                    return;
                }

                if (c == '&')
                {
                    String entity;
                    readEntity (entity);

                    if (entity.startsWithChar ('<') && entity [1] != 0)
                    {
                        auto oldInput = input;
                        auto oldOutOfData = outOfData;

                        input = entity.getCharPointer();
                        outOfData = false;

                        while (auto* n = readNextElement (true))
                            childAppender.append (n);

                        input = oldInput;
                        outOfData = oldOutOfData;
                    }
                    else
                    {
                        textElementContent << entity;
                        contentShouldBeUsed = contentShouldBeUsed || entity.containsNonWhitespaceChars();
                    }
                }
                else
                {
                    for (;; ++input)
                    {
                        auto nextChar = *input;

                        if (nextChar == '\r')
                        {
                            nextChar = '\n';

                            if (input[1] == '\n')
                                continue;
                        }

                        if (nextChar == '<' || nextChar == '&')
                            break;

                        if (nextChar == 0)
                        {
                            setLastError ("unmatched tags", false);
                            outOfData = true;
                            return;
                        }

                        textElementContent.appendUTF8Char (nextChar);
                        contentShouldBeUsed = contentShouldBeUsed || ! CharacterFunctions::isWhitespace (nextChar);
                    }
                }
            }

            if (contentShouldBeUsed)
                childAppender.append (XmlElement::createTextElement (textElementContent.toUTF8()));
        }
    }
}

void XmlDocument::readEntity (String& result)
{
    // skip over the ampersand
    ++input;

    if (input.compareIgnoreCaseUpTo (CharPointer_ASCII ("amp;"), 4) == 0)
    {
        input += 4;
        result += '&';
    }
    else if (input.compareIgnoreCaseUpTo (CharPointer_ASCII ("quot;"), 5) == 0)
    {
        input += 5;
        result += '"';
    }
    else if (input.compareIgnoreCaseUpTo (CharPointer_ASCII ("apos;"), 5) == 0)
    {
        input += 5;
        result += '\'';
    }
    else if (input.compareIgnoreCaseUpTo (CharPointer_ASCII ("lt;"), 3) == 0)
    {
        input += 3;
        result += '<';
    }
    else if (input.compareIgnoreCaseUpTo (CharPointer_ASCII ("gt;"), 3) == 0)
    {
        input += 3;
        result += '>';
    }
    else if (*input == '#')
    {
        int64_t charCode = 0;
        ++input;

        if (*input == 'x' || *input == 'X')
        {
            ++input;
            int numChars = 0;

            while (input[0] != ';')
            {
                auto hexValue = CharacterFunctions::getHexDigitValue (input[0]);

                if (hexValue < 0 || ++numChars > 8)
                {
                    setLastError ("illegal escape sequence", true);
                    break;
                }

                charCode = (charCode << 4) | hexValue;
                ++input;
            }

            ++input;
        }
        else if (input[0] >= '0' && input[0] <= '9')
        {
            int numChars = 0;

            for (;;)
            {
                const auto firstChar = input[0];

                if (firstChar == 0)
                {
                    setLastError ("unexpected end of input", true);
                    return;
                }

                if (firstChar == ';')
                    break;

                if (++numChars > 12)
                {
                    setLastError ("illegal escape sequence", true);
                    break;
                }

                charCode = charCode * 10 + ((int) firstChar - '0');
                ++input;
            }

            ++input;
        }
        else
        {
            setLastError ("illegal escape sequence", true);
            result += '&';
            return;
        }

        result << (juce_wchar) charCode;
    }
    else
    {
        auto entityNameStart = input;
        auto closingSemiColon = input.indexOf ((juce_wchar) ';');

        if (closingSemiColon < 0)
        {
            outOfData = true;
            result += '&';
        }
        else
        {
            input += closingSemiColon + 1;
            result += expandExternalEntity (String (entityNameStart, (size_t) closingSemiColon));
        }
    }
}

String XmlDocument::expandEntity (const String& ent)
{
    if (ent.equalsIgnoreCase ("amp"))   return String::charToString ('&');
    if (ent.equalsIgnoreCase ("quot"))  return String::charToString ('"');
    if (ent.equalsIgnoreCase ("apos"))  return String::charToString ('\'');
    if (ent.equalsIgnoreCase ("lt"))    return String::charToString ('<');
    if (ent.equalsIgnoreCase ("gt"))    return String::charToString ('>');

    if (ent[0] == '#')
    {
        auto char1 = ent[1];

        if (char1 == 'x' || char1 == 'X')
            return String::charToString (static_cast<juce_wchar> (ent.substring (2).getHexValue32()));

        if (char1 >= '0' && char1 <= '9')
            return String::charToString (static_cast<juce_wchar> (ent.substring (1).getIntValue()));

        setLastError ("illegal escape sequence", false);
        return String::charToString ('&');
    }

    return expandExternalEntity (ent);
}

String XmlDocument::expandExternalEntity (const String& entity)
{
    if (needToLoadDTD)
    {
        if (dtdText.isNotEmpty())
        {
            dtdText = dtdText.trimCharactersAtEnd (">");
            tokenisedDTD.addTokens (dtdText, true);

            if (tokenisedDTD[tokenisedDTD.size() - 2].equalsIgnoreCase ("system")
                 && tokenisedDTD[tokenisedDTD.size() - 1].isQuotedString())
            {
                auto fn = tokenisedDTD[tokenisedDTD.size() - 1];

                tokenisedDTD.clear();
                tokenisedDTD.addTokens (getFileContents (fn), true);
            }
            else
            {
                tokenisedDTD.clear();
                auto openBracket = dtdText.indexOfChar ('[');

                if (openBracket > 0)
                {
                    auto closeBracket = dtdText.lastIndexOfChar (']');

                    if (closeBracket > openBracket)
                        tokenisedDTD.addTokens (dtdText.substring (openBracket + 1,
                                                                   closeBracket), true);
                }
            }

            for (int i = tokenisedDTD.size(); --i >= 0;)
            {
                if (tokenisedDTD[i].startsWithChar ('%')
                     && tokenisedDTD[i].endsWithChar (';'))
                {
                    auto parsed = getParameterEntity (tokenisedDTD[i].substring (1, tokenisedDTD[i].length() - 1));
                    StringArray newToks;
                    newToks.addTokens (parsed, true);

                    tokenisedDTD.remove (i);

                    for (int j = newToks.size(); --j >= 0;)
                        tokenisedDTD.insert (i, newToks[j]);
                }
            }
        }

        needToLoadDTD = false;
    }

    for (int i = 0; i < tokenisedDTD.size(); ++i)
    {
        if (tokenisedDTD[i] == entity)
        {
            if (tokenisedDTD[i - 1].equalsIgnoreCase ("<!entity"))
            {
                auto ent = tokenisedDTD [i + 1].trimCharactersAtEnd (">").trim().unquoted();

                // check for sub-entities
                auto ampersand = ent.indexOfChar ('&');

                while (ampersand >= 0)
                {
                    auto semiColon = ent.indexOf (i + 1, ";");

                    if (semiColon < 0)
                    {
                        setLastError ("entity without terminating semi-colon", false);
                        break;
                    }

                    auto resolved = expandEntity (ent.substring (i + 1, semiColon));

                    ent = ent.substring (0, ampersand)
                           + resolved
                           + ent.substring (semiColon + 1);

                    ampersand = ent.indexOfChar (semiColon + 1, '&');
                }

                return ent;
            }
        }
    }

    setLastError ("unknown entity", true);
    return entity;
}

String XmlDocument::getParameterEntity (const String& entity)
{
    for (int i = 0; i < tokenisedDTD.size(); ++i)
    {
        if (tokenisedDTD[i] == entity
             && tokenisedDTD [i - 1] == "%"
             && tokenisedDTD [i - 2].equalsIgnoreCase ("<!entity"))
        {
            auto ent = tokenisedDTD [i + 1].trimCharactersAtEnd (">");

            if (ent.equalsIgnoreCase ("system"))
                return getFileContents (tokenisedDTD [i + 2].trimCharactersAtEnd (">"));

            return ent.trim().unquoted();
        }
    }

    return entity;
}

}
